const PARENT_LAYER_UP = 10;
const TOO_SMALL = 2;
const NON_INTERACTIVE = 0;
const CLICKABLE = 1;
const EXPANDABLE = 2;
const REMOVABLE = -1;
const INCREMENT = -2;
const DECREMENT = -3;
const PREVIOUS = -4;
const NEXT = -5;

const __ignoredTags = new Set([
    "STYLE", "SCRIPT", "NOSCRIPT",
    "OBJECT", "EMBED", "LINK", "META",
    "TEMPLATE", "HEAD"
]);
const __alreadyProcessedNodes = new Set();
const __zIndexCache = new WeakMap();
const __styleCache = new WeakMap();

// Caches top modal across invocations
let __attemptedFindTopModal = false;
let __topModalCache = null;

const DEBUG_LOG_ENABLED = true;
const LOG_VISIBILITY_CHECK = true;

function debugLog(...args) {
    if (DEBUG_LOG_ENABLED) {
        console.log(...args);
    }
}

function generateXPathJSInline(el) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return "";

    // If the node sits in a shadow-tree remember its id and
    // start walking from the immediate host instead.
    let tail = "";
    let current = el;

    const rootNode = el.getRootNode();
    if (rootNode instanceof ShadowRoot) {
        locatorStr = "locator('#SHADOW_" + el.tagName + "')";
        elId = el.id;
        if (elId) {
            locatorStr = "locator('#" + elId + "')";
        } else {
            role = getElementRole(el);
            labelText = getLabelText(el, { includeAriaLabelledBy: true, includeAriaLabel: true });
            debugLog(`Calling getLabelText after Shadow DOM detected: ${el.tagName}, id: ${elId}, role: ${role}, labelText: ${labelText}`);
            text = labelText || (el.innerText?.trim().replace(/\s+/g, ' '));
            if (role && text) {
                locatorStr = "get_by_role('" + role + "', name='" + text + "')";
            }
            else if (labelText) {
                locatorStr = "get_by_label('" + labelText + "')";
            }
        }
        tail = "/#shadow-root/" + locatorStr;
        current = rootNode.host; // start xpath construction from the host
    }

    const xpathSegments = [];
    while (current && current.nodeType === Node.ELEMENT_NODE) {
        const tag = current.tagName.toLowerCase();
        let index = 1;
        let sib = current.previousElementSibling;
        while (sib) {
            if (sib.tagName.toLowerCase() === tag) index++;
            sib = sib.previousElementSibling;
        }
        xpathSegments.unshift(`${tag}[${index}]`);

        let parent = current.parentElement;
        if (!parent) {
            const r = current.getRootNode();
            parent = r instanceof ShadowRoot ? r.host : null;
        }
        current = parent;
    }
    return "/" + xpathSegments.join("/") + tail;
}

function isRectObscured(rect, referenceEl) {
    if (isInSideIframe) return false;

    // traverse shadow DOMs to get *actual* foremost element
    function deepestElementFromPoint(x, y) {
        let el = document.elementFromPoint(x, y);
        while (el && el.shadowRoot) {
            // some shadow roots (e.g. closed ones) might not expose elementFromPoint
            const inner = el.shadowRoot.elementFromPoint?.(x, y);
            if (!inner || inner === el) break;
            el = inner;
        }
        return el;
    }

    // cross-shadow version of .contains()
    function composedContains(a, b) {
        for (let n = b; n; n = n.parentNode || (n.host ?? null)) {
            if (n === a) return true;
        }
        return false;
    }

    // run the usual checks at one probe point
    function probe(x, y) {
        const topEl = deepestElementFromPoint(x, y);
        if (!topEl) return { covered: false, blocker: null };

        let covered =
            topEl !== referenceEl &&
            !composedContains(topEl, referenceEl) &&
            !composedContains(referenceEl, topEl);

        // treat sibling stacking contexts specially
        if (
            covered &&
            topEl.parentNode &&
            Array.from(topEl.parentNode.children).some(
                sib => sib !== topEl && composedContains(sib, referenceEl)
            )
        ) {
            covered = false;
        }

        if (covered && topEl.tagName === 'IMG') covered = false;
        return { covered, blocker: covered ? topEl : null };
    }

    const p1 = probe(rect.left + rect.width / 2, rect.top);
    const p2 = probe(rect.left + rect.width / 2, rect.top + rect.height / 2);
    const p3 = probe(rect.left + rect.width / 2, rect.bottom);
    const isObscured = p1.covered && p2.covered && p3.covered;
    const blocker = isObscured ? (p2.blocker || p1.blocker || p3.blocker) : null;

    if (isObscured && isVisible(blocker, checkHasSizedChild = false)) {
        debugLog(
            `Element obscured by ${blocker.tagName}${blocker.id ? '#' + blocker.id : ''}` +
            `; classes: ${blocker.classList}; referenceEl: ${referenceEl.tagName}`
        );
        return true;
    }
    return false;
}

function isFontIcon(node) {
    const ICON_CLASSES = new Set([
        'material-icons', 'material-symbols-outlined', 'material-symbols-rounded',
        'fa', 'fa-solid', 'fa-regular', 'fa-brands',
        'bi', 'glyphicon', 'icon', 'iconfont'
    ]);

    return (
        (node.tagName === 'SPAN' || node.tagName === 'I') &&
        [...node.classList].some(cls => ICON_CLASSES.has(cls)) ||
        window.getComputedStyle(node).fontFamily.match(/material|awesome|bootstrap|icon/i)
    );
}


function getEffectiveZIndex(el) {
    if (__zIndexCache.has(el)) return __zIndexCache.get(el);

    let current = el;
    while (current && current !== document.body) {
        let style = __styleCache.get(current);
        if (!style) {
            style = window.getComputedStyle(current);
            __styleCache.set(current, style);
        }

        const z = style.zIndex;
        const parsed = parseInt(z, 10);
        if (!isNaN(parsed)) {
            __zIndexCache.set(el, parsed);
            return parsed;
        }
        current = current.parentElement;
    }

    __zIndexCache.set(el, 0);
    return 0;
}

function findTopModal() {
    const modalSelector = [
        '[role="dialog"]',
        '[aria-modal="true"]',
        '.modal',
        '.dialog',
        '.popup',
        '.overlay'
    ].join(', ');

    debugLog(`Searching for top modal with selector: ${modalSelector}`);
    const modals = Array.from(document.querySelectorAll(modalSelector)).filter(el => {
        debugLog(`Checking visibility of modal: ${el.tagName}, id: ${el.id}, class: ${el.classList}`);
        return isVisible(el, checkHasSizedChild = true, checkHiddenByModal = false);
    });

    if (modals.length === 0) return null;
    debugLog(`Found ${modals.length} visible modals, checking their z-index to see who is on top...`);

    return modals.reduce((top, el) => {
        const z = getEffectiveZIndex(el);
        return (!top || z > top.z) ? { el, z } : top;
    }, null)?.el || null;
}

function hasDescendantWithHigherZ(node, modalZ) {
    const elements = node.querySelectorAll("*[style], *[class]");
    for (const el of elements) {
        if (getEffectiveZIndex(el) > modalZ) return true;
    }
    return false;
}

function isHiddenByAnyModal(node, rect = null) {
    if (!__attemptedFindTopModal) {
        __topModalCache = findTopModal();
        __attemptedFindTopModal = true;
    }

    const topModal = __topModalCache;
    if (!topModal) return false;

    // Early returns based on DOM containment
    if (topModal.contains(node)) return false;   // node is inside the modal
    if (node.contains(topModal)) return false;   // node is an ancestor of the modal

    // Early return: bounding box doesn't overlap
    if (rect) {
        debugLog(`Checking if node overlaps with modal: ${node.tagName}, id: ${node.id}`);
        const modalRect = topModal.getBoundingClientRect();
        const overlaps = !(
            rect.bottom <= modalRect.top ||
            rect.top >= modalRect.bottom ||
            rect.right <= modalRect.left ||
            rect.left >= modalRect.right
        );

        if (!overlaps) {
            return false;
        }
    }

    const modalZ = getEffectiveZIndex(topModal);
    const nodeZ = getEffectiveZIndex(node);

    // Node is below modal and has no elevated children
    if (nodeZ < modalZ && !hasDescendantWithHigherZ(node, modalZ)) {
        return true;
    }

    return false;
}


function customHidden(node) {
    if (node.classList && (node.classList.contains('ng-binding') || node.classList.contains('completed-questionnaire'))) {
        return true;
    }
    return false;
}

function hasVisibleChild(node) {
    if (!(node instanceof Element)) return false;

    const children = node.querySelectorAll('*');
    for (const child of children) {
        const style = window.getComputedStyle(child);
        if (style.visibility === 'visible') {
            return true;
        }
    }
    return false;
}

function hasSizedChildIncludingShadow(el, tooSmall = 2) {
    const stack = [el];

    while (stack.length) {
        const node = stack.pop();

        if (node !== el && node instanceof Element) {
            const w = node.offsetWidth;
            const h = node.offsetHeight;
            if (w + h > tooSmall * 2) return true;
        }

        // Traverse light DOM
        stack.push(...node.children);

        // Traverse shadow DOM
        if (node.shadowRoot) {
            stack.push(...node.shadowRoot.children);
        }
    }

    return false;
}


function isVisible(node, checkHasSizedChild = true, checkHiddenByModal = true) {
    function logVisibleInfo(message, withSizeLog = false, visible = false) {
        if (!LOG_VISIBILITY_CHECK) return;
        elLogInfo = "";
        if (el && el instanceof Element) {
            elLogInfo = ` -- tag: ${el.tagName}, id: ${el.id}, name: ${el.name}, title: ${el.title}, class: ${el.classList}`;
        }
        if (visible == false) {
            message = "isVisible=" + visible + ": " + message + elLogInfo;
        } else {
            message = message + elLogInfo;
        }
        debugLog(message);
        if (withSizeLog) {
            debugLog(`rect: ${JSON.stringify(rect)}, offsetWidth: ${el.offsetWidth}, offsetHeight: ${el.offsetHeight}`);
        }
    }
    // If node is a text node, use node.parentElement for visibility checks
    let el = (node.nodeType === Node.TEXT_NODE) ? node.parentElement : node;
    logVisibleInfo("Starting to check visibility for element", false, true);

    if (!el || !(el instanceof Element)) {
        if (!el) {
            logVisibleInfo("Assume visible: el is null", false, true);
        } else {
            const typeStr = typeof el;
            const constructorStr = el && el.constructor ? el.constructor.name : 'unknown';
            const infoStr = `el type: ${typeStr}, constructor: ${constructorStr}`;
            logVisibleInfo("Assume visible: Element is not an instance of Element: " + infoStr, false, true);
        }
        return true;
    }
    if (el.hidden) {
        logVisibleInfo("Element has hidden attribute");
        return false;
    }
    if (customHidden(el)) {
        logVisibleInfo("Element is custom hidden");
        return false;
    }

    const style = window.getComputedStyle(el);
    if (style.display === "contents") {
        logVisibleInfo("Assume visible: Element has display: contents", false, true);
        return true;
    }

    if (style.display === "none") {
        logVisibleInfo("Element has display: none");
        return false;
    }

    if (style.visibility === "hidden" && !hasVisibleChild(el)) {
        logVisibleInfo("Element has visibility: hidden and no child overwriting it");
        return false;
    }

    if (style.clipPath !== "none" && style.clipPath !== "unset" && style.overflow === "hidden") {
        logVisibleInfo("Element has clipPath and overflow: hidden");
        return false;
    }

    const tag = el.tagName.toLowerCase();
    const isRadioOrCheckbox = tag === "input" && (el.type === "radio" || el.type === "checkbox");
    const rect = el.getBoundingClientRect();
    const isSizeNonZero = true; //el.offsetWidth > 0 || el.offsetHeight > 0 || rect.width > 0 || rect.height > 0;

    if (isRadioOrCheckbox && isSizeNonZero) {
        logVisibleInfo("Assume visible: Element is radio/checkbox with non-zero size", false, true);
        return true;
    }

    if (style.opacity === "0" && style.zIndex < 0) {
        logVisibleInfo("Element has opacity: 0 and negative z-index");
        return false;
    }
    const viewportWidth = window.innerWidth;

    // Fully offscreen
    const completelyOffscreen =
        rect.right <= 0 ||
        rect.left >= viewportWidth;

    // const physicallyTooSmall =
    //     el.offsetWidth <= TOO_SMALL &&
    //     el.offsetHeight <= TOO_SMALL &&
    //     rect.width <= TOO_SMALL &&
    //     rect.height <= TOO_SMALL;
    const physicallyTooSmall =
        el.offsetWidth === 0 ||
        el.offsetHeight === 0 ||
        rect.width === 0 ||
        rect.height === 0;

    if (physicallyTooSmall || completelyOffscreen) {
        if (style.overflow === "hidden") {
            logVisibleInfo("Element is too small or off-screen and has overflow: hidden");
            return false;
        }
        if (checkHasSizedChild) {
            const hasSizedChild = hasSizedChildIncludingShadow(el, TOO_SMALL);
            if (!hasSizedChild) {
                logVisibleInfo("Element is too small or off-screen and has no sized child", withSizeLog = true);
                return false;
            }
            logVisibleInfo("Assume visible: Element is too small or off-screen but has sized child", withSizeLog = true, visible = true);
        } else {
            logVisibleInfo("Element is too small or off-screen (no sized-child check)", withSizeLog = true);
            return false;
        }
    }

    if (checkHiddenByModal && isHiddenByAnyModal(el, rect)) {
        logVisibleInfo("Element is hidden by modal");
        return false;
    }

    return true;
}

function getElementRole(el) {
    if (!el || !(el instanceof Element)) return null;

    if ('role' in el && el.role) return el.role;

    const explicitRole = el.getAttribute('role');
    if (explicitRole) return explicitRole;

    const tag = el.tagName.toLowerCase();

    const implicitRoles = {
        'button': () => 'button',
        'a': () => el.hasAttribute('href') ? 'link' : null,
        'input': () => getInputRole(el),
        'select': () => 'combobox',
        'textarea': () => 'textbox',
        'img': () => el.hasAttribute('alt') ? 'img' : 'presentation',
        'nav': () => 'navigation',
        'main': () => 'main',
        'header': () => 'banner',
        'footer': () => 'contentinfo',
        'article': () => 'article',
        'section': () => 'region',
        'aside': () => 'complementary'
    };

    return implicitRoles[tag]?.() || null;
}

function getInputRole(input) {
    if (!(input instanceof HTMLInputElement)) return 'textbox';

    try {
        const type = (input.type || 'text').toLowerCase();
        switch (type) {
            case 'button':
            case 'submit':
            case 'reset': return 'button';
            case 'checkbox': return 'checkbox';
            case 'radio': return 'radio';
            case 'search': return 'searchbox';
            case 'email':
            case 'tel':
            case 'url': return 'textbox'; // Specialized text inputs
            case 'range': return 'slider';
            case 'number': return 'spinbutton';
            case 'image': return 'button';
            default: return 'textbox';
        }
    } catch {
        return 'textbox';
    }
}

function containsKeyword(keywords, text) {
    for (const keyword of keywords) {
        const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`\\b${escapedKeyword}\\b`, 'i');

        if (regex.test(text)) {
            return true; // Return true as soon as the first match is found
        }
    }

    // If the loop finishes without finding any matches, return false
    return false;
}

function getInteractiveLevel(el) {
    const INTERACTIVE_ROLES = new Set(["button", "link", "combobox", "menu", "menuitem", "menubar", "radio", "checkbox", "tab", "listbox", "option", "spinbutton", "textbox"]);
    if (!el || !(el instanceof Element)) return 0;
    const role = getElementRole(el);
    const tag = el.tagName.toLowerCase();
    // TO DO: handle label for <input> elements
    if (INTERACTIVE_ROLES.has(role) || tag === "button" || tag === "a") {
        const ariaExpanded = el.getAttribute("aria-expanded");
        const isCollapsed = ariaExpanded !== null && ariaExpanded == "false";
        const ariaHasPopup = el.getAttribute("aria-haspopup");
        const hasPopup = ariaHasPopup !== null && ariaHasPopup !== "false";
        // debugLog(`Checking aria attributes... tag: ${el.tagName}, role: ${role}, hasPopup: ${hasPopup} isExpanded: ${isExpanded}`);
        if (hasPopup && isCollapsed) return EXPANDABLE; // this is the expected correct behavior for documentation purpose
        if (isCollapsed) return EXPANDABLE; // we only consider aria-expanded, if dev explicitly set to false but forgot to set aria-haspopup or set it incorrectly
        if (hasPopup && ariaExpanded === null) return EXPANDABLE; // dev set aria-haspopup correctly but forgot aria-expanded

        const title = el.getAttribute("title") || "";
        const ariaLabel = el.getAttribute("aria-label") || "";
        let textContent = "";
        if (role === "button") {
            textContent = el.textContent.trim();
        }
        const accessibleText = title + " " + ariaLabel + " " + textContent;

        if (containsKeyword(["expand", "open"], accessibleText)) {
            return EXPANDABLE;
        } else if (containsKeyword(["close", "remove", "delete"], accessibleText)) {
            return REMOVABLE;
        } else if (containsKeyword(["increase", "increment", "add"], accessibleText)) {
            return INCREMENT;
        } else if (containsKeyword(["decrease", "decrement", "reduce", "subtract"], accessibleText)) {
            return DECREMENT;
        } else if (containsKeyword(["previous", "back"], accessibleText)) {
            return PREVIOUS;
        } else if (containsKeyword(["next", "forward"], accessibleText)) {
            return NEXT;
        }
        return CLICKABLE;
    } else if (
        ["editable-field", "upload-title"].some(cls => el.classList.contains(cls)) ||
        [...el.classList].some(cls => cls === "action-img" || cls.endsWith("-action-img"))) {
        return CLICKABLE;
    } else if (tag === "th" || role === "columnheader" || role === "rowheader") {
        if (el.hasAttribute("aria-sort") || (el.hasAttribute("aria-label") && el.getAttribute("aria-label").toLowerCase().includes("sort"))) {
            return CLICKABLE; // sortable table header
        }
    }
    return NON_INTERACTIVE;
}

function getInteractiveLevelTraverse(element) {
    let current = element;
    let effectiveLevel = NON_INTERACTIVE;
    let layerToCheck = 0;

    while (current && current.nodeType === Node.ELEMENT_NODE && layerToCheck < PARENT_LAYER_UP) {
        layerToCheck++;
        const level = getInteractiveLevel(current);
        if (level !== NON_INTERACTIVE && level !== CLICKABLE) {
            return level;
        } else if (level === CLICKABLE) {
            effectiveLevel = CLICKABLE;
        }
        current = current.parentElement;
    }
    return effectiveLevel;
}

function getInteractiveContentByLevel(interaLevel) {
    content = ""
    if (interaLevel === CLICKABLE) {
        content = "[B]";
    } else if (interaLevel === EXPANDABLE) {
        content = "[E]";
    } else if (interaLevel === REMOVABLE) {
        content = "[X]";
    } else if (interaLevel === INCREMENT) {
        content = "[↑]";
    } else if (interaLevel === DECREMENT) {
        content = "[↓]";
    } else if (interaLevel === PREVIOUS) {
        content = "[←]";
    } else if (interaLevel === NEXT) {
        content = "[→]";
    }
    return content;
}

function findLabelForId(shadowRoot, nodeId) {
    // Check current shadow DOM
    const label = shadowRoot.querySelector(`label[for="${nodeId}"]`);
    if (label) return label;

    // Recursively check nested shadow roots
    for (const element of shadowRoot.querySelectorAll('*')) {
        if (element.shadowRoot) {
            const found = findLabelForId(element.shadowRoot, nodeId);
            if (found) return found;
        }
    }
    return null;
}

function getLabelText(node, { includeSiblingLabel = false,
    includeAriaLabelledBy = false,
    includeAriaLabel = false,
    includeTitle = false,
    includeTextContent = false,
    includeName = false }) {
    debugLog(`getLabelText: node: ${node.tagName}, id: ${node.id}, includeSiblingLabel: ${includeSiblingLabel}, includeAriaLabelledBy: ${includeAriaLabelledBy}, includeAriaLabel: ${includeAriaLabel}, includeTitle: ${includeTitle}, includeTextContent: ${includeTextContent}, includeName: ${includeName}`);
    const nodeId = node.getAttribute('id');
    let labelText = "";

    // 1) Check <label for="ID">
    if (nodeId) {
        const labelEl = findLabelForId(document, nodeId);
        debugLog(`Checking label for ${node.tagName}, id: ${nodeId}, labelEl: ${labelEl}`);
        if (labelEl) {
            labelText = extractDirectText(labelEl);
            debugLog(`Label text found: ${labelText}`);
        }
    }

    // 2) Check if node is inside a <label>
    if (!labelText) {
        const parentLabel = node.closest('label');
        if (parentLabel) {
            labelText = extractDirectText(parentLabel);
        }
    }

    // 3) Check siblings for <label>
    if (!labelText && includeSiblingLabel && node.parentElement) {
        const siblings = Array.from(node.parentElement.children);
        for (const sibling of siblings) {
            if (sibling.tagName === 'LABEL' && isVisible(sibling)) {
                labelText = extractDirectText(sibling);
                if (labelText) break;
            }
        }
    }

    // 4) aria-labelledby — use element.innerText instead of direct text
    if (!labelText && includeAriaLabelledBy) {
        const ariaLabelledBy = node.getAttribute('aria-labelledby');
        if (ariaLabelledBy) {
            labelText = ariaLabelledBy
                .split(/\s+/)                           // multiple IDs allowed
                .map(id => document.getElementById(id))
                .filter(el => el && isVisible(el))
                .map(el => el.innerText.trim())
                .filter(txt => txt)                    // drop empties
                .join(' ');
        }
    }

    if (!labelText && includeAriaLabel) {
        // 5) Check for aria-label
        const ariaLabel = node.getAttribute('aria-label');
        if (ariaLabel) {
            labelText = ariaLabel.trim();
        }
    }

    if (!labelText && includeTitle) {
        // 6) Check for title attribute
        const title = node.getAttribute('title');
        if (title) {
            labelText = title.trim();
        }
    }

    if (!labelText && includeTextContent) {
        // 7) Check for textContent
        labelText = node.textContent.trim();
    }

    if (!labelText && includeName) {
        // 8) Check for name attribute
        const name = node.getAttribute('name');
        if (name) {
            labelText = name.trim();
        }
    }
    return labelText ? labelText.replace(/[\r\n\s]+/g, ' ').trim() : "";
}

function extractDirectText(element) {
    return Array.from(element.childNodes)
        .filter(node => node.nodeType === Node.TEXT_NODE)
        .map(textNode => textNode.textContent.trim())
        .join(' ') // Combine adjacent text nodes
        .replace(/\s+/g, ' '); // Normalize whitespace
}

function isFillableTdCell(td) {
    if (!td || td.tagName !== 'TD') return false;

    const row = td.parentElement;
    if (!row || row.tagName !== 'TR') return false;

    const tds = Array.from(row.querySelectorAll('td'));
    const index = tds.indexOf(td);

    if (index > 0) {
        const left = tds[index - 1];
        return (
            // left.textContent.trim().length > 0 &&
            left.classList.contains('ht-gray') &&
            !td.classList.contains('ht-gray')
        );
    }

    // first td — no left neighbor
    return false;
}

function addSegment({ type, content = undefined, x, y, width, height, xpath, enclose = undefined, id = undefined, labelText = undefined }) {
    const segment = { type, x, y, width, height, xpath };
    if (content !== undefined) segment.content = content;
    if (enclose !== undefined) segment.enclose = enclose;
    if (id !== undefined) segment.id = id;
    if (labelText !== undefined) segment.labelText = labelText;
    segments.push(segment);
}

function traverse(node) {
    if (!node || __alreadyProcessedNodes.has(node) || __ignoredTags.has(node.tagName)) return;
    if (node.nodeType === Node.COMMENT_NODE) return;

    if (!isVisible(node)) {
        debugLog(`Stop Traversing and Skipping invisible node: ${node.tagName}, id: ${node.id}, class: ${node.classList}`);
        return;
    }

    if (node.nodeType === Node.TEXT_NODE) {
        // Combine with consecutive text nodes, skipping blanks
        let combinedText = node.textContent.trim();
        if (!combinedText) return;
        let next = node.nextSibling;
        while (next && next.nodeType === Node.TEXT_NODE) {
            // because we are processing text sibling nodes here, not through the traverse
            // we need to indicate we have already processed this node
            __alreadyProcessedNodes.add(next);
            if (isVisible(next)) combinedText += next.textContent.trim();
            next = next.nextSibling;
        }

        const parent = node.parentElement;
        if (!parent) return;
        const parentRect = parent.getBoundingClientRect();
        let rect;
        if (parent.tagName.toLowerCase() === 'td') {
            debugLog(`Using parent's bounding box for td or combined text nodes: ${combinedText}`);
            rect = parentRect;
        } else {
            const range = document.createRange();
            range.selectNodeContents(node);
            rect = range.getBoundingClientRect();
            if (rect.width > parentRect.width || rect.height > parentRect.height) {
                rect.width = parentRect.width;
                rect.height = parentRect.height;
            }
        }
        if (isRectObscured(rect, parent)) return;

        combinedText = combinedText.replace(/&nbsp;|\s+/g, ' ').trim();

        interaLevel = getInteractiveLevelTraverse(parent);
        // icon not nested under button or anchor
        if (isFontIcon(parent)) {
            const iconText = getInteractiveContentByLevel(interaLevel) || "[B]"
            const labelText = getLabelText(parent, {
                includeAriaLabel: true,
                includeTitle: true,
                includeTextContent: true
            });
            addSegment({
                type: 'text',
                content: iconText,
                enclose: 0,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(parent),
                labelText: labelText
            });
            return;
        }
        if (combinedText) {
            addSegment({
                type: 'text',
                content: combinedText,
                enclose: interaLevel,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(parent)
            });
        }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
        // If it's an iframe, store a reference so we can recurse in Python
        if (node.tagName.toLowerCase() === "iframe") {
            let frameId = "FRAME_" + counter++;
            node.setAttribute("data-frame-id", frameId);
            let rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) {
                debugLog("Obscured iframe: " + frameId);
                return;
            }
            addSegment({
                type: 'iframe',
                id: frameId,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(node)
            });
            return;
        } else if (node.tagName.toLowerCase() === 'input' ||
            node.tagName.toLowerCase() === 'select' ||
            node.tagName.toLowerCase() === 'textarea') {

            let inputType;
            if (node.tagName.toLowerCase() === 'input') {
                inputType = (node.getAttribute('type') || 'text').toLowerCase();
            }

            let rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) {
                debugLog("Obscured input/select: " + node.tagName + ", id: " + node.id);
                return;
            }
            if (rect.width === 0 || rect.height === 0) {
                rect.width = node.offsetWidth;
                rect.height = node.offsetHeight;
            }
            let content = "";
            if (inputType === "text" || inputType === "password" || inputType === "search" || inputType === "number" ||
                inputType === "email" || inputType === "tel" || inputType === "range" ||
                node.tagName.toLowerCase() === 'textarea') {
                let val = node.value || "";
                if (!val.trim()) {
                    let placeholder = node.getAttribute('placeholder') || "";
                    if (placeholder.trim()) {
                        // Use placeholder if present
                        val = placeholder;
                    } else {
                        let labelText = getLabelText(node, { includeAriaLabelledBy: true, includeAriaLabel: true, includeTitle: true, includeTextContent: true, includeName: true });
                        debugLog("Calling getLabelText for input with no value and placeholder: " + node.tagName + ", type: " + inputType + ", id: " + node.id + ", labelText: " + labelText);
                        if (labelText.trim()) {
                            val = labelText;
                        } else {
                            val = "Input data here";
                        }
                    }
                }
                content = "{" + val + "}";
            } else if (inputType === "checkbox") {
                debugLog("Checkbox type: " + inputType + ", id: " + node.id);
                content = "☐";
                if (node.checked) {
                    content = "✅";
                }
            } else if (inputType === "radio") {
                content = "🔘";
                if (node.checked) {
                    content = "🟢";
                }
            } else if (node.tagName.toLowerCase() === 'select') {
                // If it's a <select>, get the selected option text
                let selectedOption = node.querySelector('option:checked');
                let val = (selectedOption ? selectedOption.textContent.trim() : "");

                if (!val) {
                    let labelText = getLabelText(node, {});
                    debugLog("Calling getLabelText for select with no selected Option: " + node.tagName + ", id: " + node.id + ", labelText: " + labelText);
                    val = labelText || "No option selected";
                }
                content = "{{" + val + "}}";
                options = node.querySelectorAll('option');
                for (let option of options) {
                    let optionText = option.textContent.trim() || node.value;
                    if (optionText === val) continue; // Skip the selected option
                    content += `|| - ${optionText}`;
                }
            } else {
                content = ""
            }
            if (content) {
                debugLog("Pushing input node: " + content);
                addSegment({
                    type: 'input',
                    content: content,
                    x: rect.left,
                    y: rect.top,
                    width: rect.width,
                    height: rect.height,
                    xpath: generateXPathJSInline(node)
                });                
                // After handling an <input>, we don't descend into its children
                // (since an <input> typically doesn't have child text nodes to handle)
                return;
            }
        }
        // Handle <a> <button> elements
        if (getElementRole(node) === 'button' || getElementRole(node) === 'link' ||
            node.tagName.toLowerCase() === 'button' || node.tagName.toLowerCase() === 'a' ||
            node.tagName.toLowerCase() === 'img' || node.tagName.toLowerCase() === 'svg') { // ||
            // getElementRole(node) === 'menuitem' || getElementRole(node) === 'tab' ||
            // getElementRole(node) === 'option') {
            // group child text nodes
            // this is the bounding box for this element node
            // need to adjust it to the first text node bounding box later
            const elementNodeRec = node.getBoundingClientRect();
            if (isRectObscured(elementNodeRec, node)) return;
            let content;
            const interaLevel = getInteractiveLevelTraverse(node);
            // Extract visible and invisible text nodes
            const visibleTextParts = [];

            const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
            while (walker.nextNode()) {
                const textNode = walker.currentNode;
                const trimmed = textNode.textContent.trim();
                if (!trimmed) continue;
                const parentEl = textNode.parentElement;
                if (isVisible(parentEl) && !isFontIcon(parentEl)) {
                    visibleTextParts.push(trimmed);
                } else {
                    __alreadyProcessedNodes.add(textNode);
                }
            }
            let visibleText = visibleTextParts.join(' ').trim().replace(/[\r\n\s]+/g, ' ');

            if (!visibleText) { // icon or svg or other buttons/anchors without text
                debugLog("Empty button/anchor: " + node.tagName + ", id: " + node.id + ", aria-label: " + node.ariaLabel + ", title: " + node.title);
                if (node.hasAttribute('disabled')) return;
                // Check for any image with alt (even aria-hidden ones)
                const hasAnyImage = !!node.querySelector('img');
                let inFigureWithImage = false;
                let current = node.parentElement;
                while (current) {
                    if (current.tagName.toLowerCase() === 'figure') {
                        inFigureWithImage = !!current.querySelector('img');
                        break; // Stop at the first figure
                    }
                    current = current.parentElement;
                }
                if (hasAnyImage || inFigureWithImage) {
                    content = "[IMG]";
                } else {
                    const fallbackValue = node.getAttribute("value") || "";
                    if (fallbackValue) {
                        content = `[${fallbackValue}]`;
                    } else {
                        content = getInteractiveContentByLevel(interaLevel);
                    }
                }

                // Check for image label
                let labelText = '';
                const imageWithAlt = Array.from(node.querySelectorAll('img[alt]')).find(img => {
                    const alt = img.getAttribute('alt')?.trim();
                    const ariaHidden = img.getAttribute('aria-hidden')?.toLowerCase();
                    return alt && ariaHidden !== 'true';
                });
                const svgWithAriaLabel = Array.from(node.querySelectorAll('svg[aria-label]')).find(svg => {
                    const ariaLabel = svg.getAttribute('aria-label')?.trim();
                    const ariaHidden = svg.getAttribute('aria-hidden')?.toLowerCase();
                    return ariaLabel && ariaHidden !== 'true';
                });
                if (imageWithAlt) {
                    labelText = imageWithAlt.getAttribute('alt').trim();
                    debugLog(`Empty button/anchor: Used <img alt> for labelText: "${labelText}"`);
                } else if (svgWithAriaLabel) {
                    labelText = svgWithAriaLabel.getAttribute('aria-label').trim();
                    debugLog(`Empty button/anchor: Used <svg aria-label> for labelText: "${labelText}"`);
                } else {
                    labelText = getLabelText(node, {
                        includeAriaLabel: true,
                        includeTitle: true,
                        includeTextContent: true
                    });
                    debugLog(`Empty button/anchor: getLabelText result: "${labelText}"`);
                }
                addSegment({
                    type: 'text',
                    content: content,
                    enclose: 0,
                    x: elementNodeRec.left,
                    y: elementNodeRec.top,
                    width: elementNodeRec.width,
                    height: elementNodeRec.height,
                    xpath: generateXPathJSInline(node),
                    labelText: labelText
                });
                return;
            }
        } else if (
            (getElementRole(node) === 'textbox' || getElementRole(node) === 'combobox') &&
            node.hasAttribute('contenteditable') &&
            node.getAttribute('contenteditable')?.toLowerCase() !== 'false'
        ) {
            // Handle contenteditable elements
            const rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) return;
            let text = node.textContent.trim();
            if (!text) {
                text = node.getAttribute('placeholder') || "Input data here";
            }

            text = `{${text.replace(/[{}]/g, '')}}`;
            addSegment({
                type: 'text',
                content: text,
                enclose: 0,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(node)
            });
            return; // Don't traverse children of contenteditable elements
        } else if (getElementRole(node) === 'option') {
            const rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) return;
            const text = node.innerText.trim().replace(/[\r\n\s]+/g, ' ');
            addSegment({
                type: 'text',
                content: text,
                enclose: getInteractiveLevelTraverse(node),
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(node)
            });
            return;
        }

        // TODO: Better handling of customization
        if (node.classList && node.classList.contains('hot-container') &&
            !node.closest('.modal-hot-container') // ✅ skip if inside modal-body
        ) {
            const rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) return;
            addSegment({
                type: 'text',
                content: "[Click To Edit]",
                enclose: 0,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(node)
            });
        }

        if (node.tagName.toLowerCase() === 'td' &&
            node.parentElement?.tagName.toLowerCase() === 'tr' &&
            node.closest('hot-table') && // ✅ ensure it's inside a <hot-table>
            node.closest('.modal-hot-container')) { // ✅ ensure it's inside a modal-hot-container
            const rect = node.getBoundingClientRect();
            if (isRectObscured(rect, node)) return;
            textContent = node.textContent.trim();
            if (isFillableTdCell(node)) {
                if (!textContent) {
                    textContent = "Fill Data"
                }
                textContent = "{" + textContent + "}";
            }
            addSegment({
                type: 'text',
                content: textContent,
                enclose: 0,
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height,
                xpath: generateXPathJSInline(node)
            });
            return;
        }

        // Recursively descend for other visible elements
        if (node.shadowRoot) {
            debugLog("Shadow DOM detected: " + node.tagName + ", id: " + node.id);
            traverse(node.shadowRoot);
        }
        for (let child of node.childNodes) {
            traverse(child);
        }
    } else if (node.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
        for (let child of node.childNodes) {
            traverse(child);
        }
    }
}

let counter = 0;
let segments = [];
traverse(document.body);   
