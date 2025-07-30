import re
import json
import asyncio
import math
import base64
import subprocess
import os
import random
from playwright.async_api import Locator
from typing import Dict, Tuple

import surfari.config as config
import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)

screenshot_lock = asyncio.Lock()

def remove_unescaped_control_characters(json_str):
    """
    Remove unescaped control characters (ASCII 0-31) from a JSON string.

    This function uses a regex to find control characters (characters in the range
    U+0000 to U+001F) that are not already escaped (i.e. not immediately preceded by a backslash)
    and removes them.

    Note: This may result in loss of some whitespace formatting in string values.
    """
    # The regex (?<!\\)[\x00-\x1F] matches any control character not preceded by a backslash.
    pattern = re.compile(r"(?<!\\)[\x00-\x1F]")
    return pattern.sub("", json_str)


def fix_playwright_locators(locators_dict):
    """
    Takes a dictionary of locators and ensures all locator strings are valid Playwright locators.

    - If it's a CSS selector (starts with '#' or '.'), wraps it in `page.locator()`.
    - If it's an XPath locator (starts with '//' or '('), wraps it in `page.locator('xpath=...')`.
    - If it's a Playwright locator (`page.locator(...)`, `page.get_by_*()`, `page.frame_locator(...)`), it remains unchanged.
    - If it's a raw text like "Log in", converts it to `page.get_by_text("Log in")`.
    - If the locator format is incorrect, logs a warning and sets it to None.

    Args:
        locators_dict (dict): Dictionary where keys are locator names and values are locator strings.

    Returns:
        dict: Dictionary with corrected locator strings.
    """
    fixed_locators = {}

    for locator_name, locator_str in locators_dict.items():
        if locator_name == "site_id":
            continue
        if not locator_str or not isinstance(locator_str, str):
            logger.error(
                f"[{locator_name}] Invalid locator: Must be a non-empty string."
            )
            fixed_locators[locator_name] = None
            continue

        locator_str = locator_str.strip()

        # Already a valid Playwright locator (including get_by_* and frame_locator)
        if locator_str.startswith(
            ("page.locator(", "page.get_by_", "page.frame_locator(")
        ):
            logger.debug(
                f"[{locator_name}] Already a valid Playwright locator: {locator_str}"
            )
            fixed_locators[locator_name] = locator_str
            continue

        # CSS Selectors (#id, .class)
        if locator_str.startswith("#") or locator_str.startswith("."):
            logger.debug(f"[{locator_name}] Identified as CSS selector: {locator_str}")
            fixed_locators[locator_name] = f'page.locator("{locator_str}")'
            continue

        # XPath locators
        if locator_str.startswith("//") or locator_str.startswith("("):
            logger.debug(f"[{locator_name}] Identified as XPath: {locator_str}")
            fixed_locators[locator_name] = f'page.locator("xpath={locator_str}")'
            continue

        # Role-based locators (e.g., "button[name='Login']")
        if re.match(
            r"^\w+\[", locator_str
        ):  # Detects attributes like button[name="Login"]
            logger.debug(
                f"[{locator_name}] Identified as role-based selector: {locator_str}"
            )
            fixed_locators[locator_name] = f'page.locator("{locator_str}")'
            continue

        # Best-effort: Detect standalone text and use `page.get_by_text()`
        if re.match(r"^[a-zA-Z0-9\s'\"!@#$%^&*()_+=-]+$", locator_str):
            logger.debug(
                f"[{locator_name}] Identified as text-based selector: {locator_str}"
            )
            fixed_locators[locator_name] = f'page.get_by_text("{locator_str}")'
            continue

        # Unknown format - Log a warning and set to None
        logger.warning(
            f"[{locator_name}] Unrecognized locator format: {locator_str}. Setting to None."
        )
        fixed_locators[locator_name] = None

    return fixed_locators


async def wait_for_page_load_generic(page, timeout_ms=1000, post_load_timeout_ms=2000):
    """
    Waits for page to load, stabilize DOM, and final JavaScript execution.

    Args:
        page: Playwright page object.
        timeout_ms: Max time to wait in milliseconds.
        post_load_timeout_ms: Final buffer after load.
    """
    import asyncio
    import time
    start_time = time.time()
    try:
        # 1. Wait for 'load' event
        await page.wait_for_load_state("load", timeout=timeout_ms)
        logger.debug("Page load state 'load' reached.")

        # 2. Wait for DOM stabilization
        dom_stable = await wait_for_dom_stable(page, timeout=timeout_ms)
        logger.debug("Page load state DOM structure stabilized.")
        
        # 3. Wait for network idle
        network_idle_timeout = config.CONFIG["app"].get("network_idle_timeout", -1)
        if network_idle_timeout > 0:
            logger.debug("Waiting for 'networkidle' state...")
            await page.wait_for_load_state("networkidle", timeout=network_idle_timeout)
            logger.debug("Page load state 'networkidle' reached.")
            
    except Exception as e:
        logger.error(f"Page load state failed: {e}")

    if (post_load_timeout_ms > 0):
        await asyncio.sleep(post_load_timeout_ms / 1000)
        logger.debug(f"Page load state compensation timeout of {post_load_timeout_ms}ms completed.")
        
    total_time = time.time() - start_time
    logger.debug(f"Page load state total complete after {total_time:.2f} seconds.")

async def wait_for_dom_stable(page, timeout=3000):
    import asyncio
    import time

    logger.debug("Polling DOM element count manually...")

    start_time = time.time()
    end_time = start_time + timeout / 1000

    prev_count = None

    while time.time() < end_time:
        try:
            count = await page.evaluate("document.querySelectorAll('*').length")
            if prev_count is not None and count == prev_count:
                logger.debug(f"DOM element count stabilized at {count}")
                return True
            prev_count = count
        except Exception as e:
            logger.warning(f"Error while polling DOM elements: {e}")
        
        await asyncio.sleep(0.2)  # Poll every 200ms

    raise TimeoutError("DOM stabilization timed out.")

async def take_actions(page, locator_actions, num_steps=1, is_iterative=False) -> list[dict]:
    """
    Execute a series of actions on a page using Playwright.

    Args:
        locator_actions: a JSON string or object containing a list of locator actions to perform.
            Each locator action should be a dictionary with the following keys:
            - "action": The action to perform (e.g., "click", "fill", "select").
            - "locator": The locator string or locator object for the element to interact with.
            - "value": The value to fill or select (optional).

    Returns:
        a list of locator actions with their execution results.
    """
    logger.trace(f"Performing actions on page with locator actions: {locator_actions}")
    logger.debug(f"Number of steps to perform: {num_steps}")
    logger.debug(f"Is Iterative execution: {is_iterative}")
    
    if isinstance(locator_actions, str):
        locator_actions = remove_unescaped_control_characters(locator_actions)
        locator_actions = json.loads(locator_actions)

    # if somehow action is not a list but a dict, convert it to a list
    if not isinstance(locator_actions, list):     
        locator_actions = [locator_actions]
        
    # extract the list of just locators from locator_actions
    locators = [action.get("locator") for action in locator_actions if "locator" in action]
    try:
        await highlight_elements(page=page, elements=locators, color="red", duration=1000)
    except Exception as e:
        logger.error(f"Error highlighting elements: {e}")
    
    skip_subsequent_actions = False
    for i, locator_action in enumerate(locator_actions, start=1):
        action_name = f"locator_action {i}"
        if skip_subsequent_actions:
            logger.debug(f"{action_name}: Skipping subsequent actions due to previous action.")
            locator_action["result"] = "Wait: The last successful action caused the page to show/hide elements. You need to re-evaluate based on the current page content."
            break
                
        logger.sensitive(f"Examining and performing {action_name}: {locator_action}")

        is_expandable_element = locator_action.get("is_expandable_element", False)
        if is_expandable_element:
            skip_subsequent_actions = True
        
        action = locator_action.get("action")
        locator = locator_action.get("locator")
        value = locator_action.get("value")        
        if not action:
            logger.warning(f"{action_name}: No action provided. Skipping.")
            locator_action["result"] = "Error: No action provided"
            continue
        
        if not locator:
            logger.warning(f"{action_name}: No locator provided. Skipping.")
            locator_action["result"] = "Error: No locator provided"
            continue

        if action in ("fill", "select") and not value:
            logger.warning(f"{action_name}: No value provided for {action}.")
            locator_action["result"] = "Error: No value provided"
            continue

        try:
            if isinstance(locator, str):
                element = eval(locator)
            elif isinstance(locator, Locator):
                element = locator
            else:
                logger.warning(f"{action_name}: Invalid locator type. Skipping.")
                locator_action["result"] = "Error: Invalid locator type"
                continue
            
            element_count = await element.count()            
            if element_count == 0:
                logger.warning(f"{action_name}: Element not found. Skipping.")
                locator_action["result"] = "Error: Element not found"
                continue

            # If multiple elements found, look for the first visible one
            if element_count > 1:
                visible_element = None
                for i in range(element_count):
                    current_element = element.nth(i)
                    if await current_element.is_visible():
                        visible_element = current_element
                        break
                
                if visible_element:
                    element = visible_element
                else:
                    logger.info(f"{action_name}: Multiple elements found but none visible, using first element")
                    element = element.first()

        except Exception as e:
            logger.error(f"{action_name}: Error eval-ing locator: {e}")
            locator_action["result"] = f"Error: Invalid locator: {e}"
            continue

        element_disabled = await element.is_disabled()
        if element_disabled:
            logger.warning(f"{action_name}: Element is disabled. Skipping.")
            locator_action["result"] = "Error: Element is currently disabled. You should try something else"
            continue
            
        try:
            try:
                logger.debug(f"{action_name}: Attempting to scroll element into view and move mouse")
                await element.scroll_into_view_if_needed(timeout=2000)
                await element.wait_for(timeout=2000, state="visible")
                await move_mouse_to(element)
                logger.debug("Successfully scrolled element into view, element is visible, and mouse moved")
            except Exception as e:
                logger.error(f"{action_name}: Will force after encountering error preparing for action: {e}")
                
            if action == "click":
                if True: # for now, always do this
                    try:
                        await element.click(timeout=10000, force=True)
                        logger.debug(f"{action_name}: Clicked element using Playwright click")
                    except Exception as e:
                        logger.error(f"{action_name}: Retry with direct JS evaluate after error force clicking element: {e}")
                        y_pos = await locator.evaluate("el => el.getBoundingClientRect().top + window.scrollY")
                        await page.evaluate(f"() => window.scrollTo(0, {int(y_pos) - 100})")
                        await locator.evaluate("""
                        el => {
                            const event = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            el.dispatchEvent(event);
                        }
                        """)
                        logger.debug(f"{action_name}: Clicked element using JS evaluate")                        

            elif action == "fill":
                await element.click(timeout=2000, force=True)
                tag_name = await element.evaluate("el => el.tagName", timeout=2000)
                if tag_name and tag_name.lower() == "td":
                    await element.dblclick(timeout=2000, force=True)
                    logger.debug(f"{action_name}: Double clicked td element to edit")
                    # customization for handsontable
                    input_locator = page.locator('textarea.handsontableInput[data-hot-input]')
                    await input_locator.fill(value, timeout=2000, force=True)
                else:
                    dom_element_count_before = await page.evaluate("document.querySelectorAll('*').length")
                    type = await element.evaluate("el => el.type", timeout=2000)    
                    if type and type.lower() == "number":
                        # If the input is a number, fill it with the value
                        await element.fill(value, timeout=2000, force=True)
                    else:
                        await element.clear(timeout=2000, force=True) 
                        await page.wait_for_timeout(300)  # Wait for .3 second before typing           
                        # For other types, use press_sequentially
                        # await element.fill(value, timeout=2000, force=True)
                        await element.press_sequentially(value, delay=50)
                    dom_element_count_after = await page.evaluate("document.querySelectorAll('*').length")
                    if dom_element_count_after != dom_element_count_before:
                        logger.debug(f"{action_name}: Skipping subsequent actions because DOM element count changed after fill: {dom_element_count_after} (before: {dom_element_count_before})")
                        # skip_subsequent_actions = True
                    else:
                        logger.debug(f"{action_name}: DOM element count unchanged after fill: {dom_element_count_after}")
            elif action == "select":
                await element.select_option(value, timeout=10000, force=True)
            elif action == "check":
                try:
                    await element.check(timeout=1000, force=True)
                except Exception as e:
                    await element.evaluate("""
                    el => {
                        let match = el.closest('mat-checkbox, [role="checkbox"], label, [role="radio"], input[type="checkbox"], input[type="radio"]');
                        // console.log('[closest check]', match);
                        if (match) match.click();
                    }
                    """)

            elif action == "uncheck":
                try:
                    await element.uncheck(timeout=1000, force=True)
                except Exception as e:
                    await element.evaluate("""
                    el => {
                        let match = el.closest('mat-checkbox, [role="checkbox"], label, [role="radio"], input[type="checkbox"], input[type="radio"]');
                        // console.log('[closest check]', match);
                        if (match) match.click();
                    }
                    """)                                        
            elif action == "dbclick":
                await element.dblclick(timeout=1000, force=True)
            else:
                logger.warning(f"{action_name}: Unsupported action: {action}. Skipping.")
                locator_action["result"] = f"Error: Unsupported action: {action}"
                continue

            locator_action["result"] = "success"
            await page.wait_for_timeout(2000)  # Wait for 2 second after each action
        except Exception as e:
            logger.error(f"{action_name}: Error performing action: {e}")
            locator_action["result"] = f"Error: failed to perform action: {e}"
        
        if i == num_steps:
            break
      
    return locator_actions


async def capture_full_page_screenshot_via_cdp(context, page, filepath=None, timeout=10):
    client = await context.new_cdp_session(page)

    # 1) Save the current viewport so we can restore later (optional)
    orig_width = context.pyautogui_screen_width
    orig_height = context.pyautogui_screen_height
    logger.debug(f"Original viewport at startup time: {orig_width}x{orig_height}")

    # 2) Get layout metrics to see the full page content size
    metrics = await client.send("Page.getLayoutMetrics")
    content_size = metrics["contentSize"]
    width = math.ceil(content_size["width"])
    height = math.ceil(content_size["height"])
    logger.debug(f"Page.getLayoutMetrics: full content size: {width}x{height}")
    
    # keep the orig_width and cap height at 3 times the original height
    width = orig_width
    height = min(height, 3 * orig_height)

    screenshot = None
    bring_to_front_called = False
    try:
        # 3) Override the device metrics for full-page screenshot
        async with screenshot_lock:
            logger.debug(f"taking screenshot step 1: Emulation.setDeviceMetricsOverride size: {width}x{height}")
            await client.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
            # 4) Capture full screenshot with 'clip'
            await asyncio.sleep(1)
            logger.debug(f"taking screenshot step 2: captureScreenshot")
            screenshot = await asyncio.wait_for(
                client.send(
                    "Page.captureScreenshot",
                    {
                        "format": "png", 
                        "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1}
                        # "captureBeyondViewport": True
                    }
                ),
                timeout=timeout  # seconds
            )
    except asyncio.TimeoutError:
        async with screenshot_lock:      
            logger.debug(f"retry taking screenshot step 1: bring to front")
            await client.send("Page.bringToFront")
            logger.debug(f"retry taking screenshot step 2: Emulation.setDeviceMetricsOverride size: {width}x{height}")
            await client.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})  
            await asyncio.sleep(1)            
            logger.debug(f"retry taking screenshot step 3: captureScreenshot")            
            screenshot = await client.send(
                "Page.captureScreenshot",
                {
                    "format": "png", 
                    "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1}
                    # "captureBeyondViewport": True
                }
            )
            logger.debug(f"retry taking screenshot step 4: hideOrShowWindow")            
            await hideOrShowWindow(context, page) 
  
    if screenshot and filepath:
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(screenshot["data"]))
    return screenshot

async def hideOrShowWindow(context=None, page=None):
    run_in_background = (
        config.CONFIG["app"]["run_in_background"]
        or os.getenv("SURFARI_IN_BACKGROUND", "False").lower() == "true"
    )
    if not run_in_background:
        return    
     
    if context and page:
        logger.info("Minimizing window after launch with CDP")
        client = await context.new_cdp_session(page)
        window_info = await client.send("Browser.getWindowForTarget")
        window_id = window_info["windowId"]
        await client.send(
            "Browser.setWindowBounds",
            {
                "windowId": window_id,
                "bounds": {
                    "windowState": "minimized",
                },
            },
        )
    else:
        process_name = "Chromium"
        script = f'tell application "System Events" to set visible of process "{process_name}" to false'

        try:
            logger.info("Trying to hide the window after launch")
            logger.info(script)
            subprocess.run(["osascript", "-e", script], check=True)
        except subprocess.CalledProcessError as error:
            logger.error(f"Error hide window: {error}")

async def move_mouse_to(locator):
    if not await locator.is_visible():
        logger.error(f"Can't move mouse to locator as it is not visible: {locator}")
        return
    
    box = await locator.bounding_box()
    if box:
        x = box["x"] + box["width"] * random.uniform(0, 2) / 2
        y = box["y"] + box["height"] * random.uniform(0, 2) / 2
        await locator.page.mouse.move(x, y, steps=int(random.uniform(0, 5)) + 1)


async def scroll_main_scrollable_down_and_up(page, no_of_scrolls=10) -> bool:
    count = 0
    scrolled = scrolled_started = await scroll_main_scrollable(page) 
    while scrolled and count < no_of_scrolls:
        scrolled = await scroll_main_scrollable(page) 
        count += 1
    if scrolled_started:
        await page.wait_for_timeout(1000)  # Wait for 1 second after scrolling down
        await scroll_main_scrollable(page, to_top=True)
                    
async def scroll_main_scrollable(page, to_top: bool = False) -> bool:
    locator, scrollable_element = await get_main_scrollable_locator(page)
    if not locator:
        logger.warning("No scrollable element found.")
        return False

    logger.info(f"Scrolling {'to top' if to_top else 'to bottom'} of: {scrollable_element}")

    before = await locator.evaluate("el => el.scrollTop")

    scroll_script = """
        (el, toTop) => {
            const target = toTop ? 0 : el.scrollHeight - el.clientHeight;
            el.scrollTo({ top: target, behavior: 'smooth' });
            console.log('[scroll]', `Smooth scroll to: ${target}`);
        }
    """
    await locator.evaluate(scroll_script, to_top)

    await page.wait_for_timeout(50)

    after = await locator.evaluate("el => el.scrollTop")
    logger.info(f"[scroll] Scrolled from {before} to {after}")

    return after != before if to_top else after > before
    
    
async def list_scrollable_elements(page):
    return await page.evaluate("""
    () => {
        function isScrollable(el) {
            const style = getComputedStyle(el);
            return (style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                   el.scrollHeight > el.clientHeight;
        }

        const scrollables = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
        let node = walker.nextNode();
        while (node) {
            if (isScrollable(node)) {
                scrollables.push({
                    tag: node.tagName,
                    id: node.id || null,
                    class: Array.from(node.classList),
                    scrollHeight: node.scrollHeight,
                    clientHeight: node.clientHeight
                });
            }
            node = walker.nextNode();
        }

        // Also consider document-level scrolling
        const doc = document.scrollingElement || document.body;
        if (doc.scrollHeight > doc.clientHeight) {
            scrollables.push({
                tag: doc.tagName,
                id: doc.id || null,
                class: Array.from(doc.classList),
                scrollHeight: doc.scrollHeight,
                clientHeight: doc.clientHeight
            });
        }
        // Sort by scrollHeight descending
        scrollables.sort((a, b) => b.scrollHeight - a.scrollHeight);
        return scrollables;
    }
    """)
    
def css_escape(s: str) -> str:
    # Escape special characters in CSS class names
    return re.sub(r'([^\w-])', lambda m: "\\" + m.group(1), s)

async def get_main_scrollable_locator(page) -> Tuple[Locator, Dict]:
    scrollables = await list_scrollable_elements(page)
    locator = None
    for i, scrollable_element in enumerate(scrollables):
        tag = scrollable_element["tag"]
        id_ = scrollable_element["id"]
        classes = scrollable_element["class"]

        logger.info(f"Scrollable element {i}: {scrollable_element}")

        # Try to create locator
        if id_:
            locator = page.locator(f"#{id_}")
        elif classes:
            escaped_classes = [css_escape(cls) for cls in classes]
            class_selector = "." + ".".join(escaped_classes)
            locator = page.locator(f"{tag}{class_selector}")
        else:
            locator = page.locator(tag)
        # await highlight_elements(page, [locator])
        return locator, scrollable_element # Only get the main (largest) one
    return None, {}

async def highlight_elements(page, elements, color="red", duration=500):
    """Highlight elements with a colored outline"""
    for element in elements:
        await element.evaluate(f"el => el.style.outline = '3px solid {color}'")
    await page.wait_for_timeout(duration)
    for element in elements:
        await element.evaluate("el => el.style.outline = ''")


async def inject_control_bar(page, message: str = ""):
    js_code = f"""
    (() => {{
        const controlBar = document.createElement('div');
        controlBar.id = "surfari-control-bar";
        controlBar.style.position = 'fixed';
        controlBar.style.bottom = '0';
        controlBar.style.left = '0';
        controlBar.style.right = '0';
        controlBar.style.zIndex = '9999';
        controlBar.style.color = 'black';
        controlBar.style.padding = '10px';
        controlBar.style.fontSize = '14px';
        controlBar.style.display = 'flex';
        controlBar.style.alignItems = 'center';
        controlBar.style.backgroundColor = 'lightgray';
        controlBar.style.fontFamily = 'Arial, sans-serif';
        controlBar.style.boxShadow = '0px -2px 5px rgba(0,0,0,0.2)';
        
        const statusContainer = document.createElement('div');
        statusContainer.style.display = 'flex';
        statusContainer.style.alignItems = 'center';

        const messageSpan = document.createElement('span');
        messageSpan.textContent = {message!r};
        messageSpan.style.fontSize = '16px';
        messageSpan.style.fontWeight = 'bold';
        messageSpan.style.color = '#333';
        messageSpan.style.marginRight = '24px';
        statusContainer.appendChild(messageSpan);

        const toggleButton = document.createElement('button');
        toggleButton.textContent = 'Toggle Mode';
        toggleButton.style.marginLeft = 'auto';
        toggleButton.style.padding = '5px 12px';
        toggleButton.style.border = 'none';
        toggleButton.style.borderRadius = '4px';
        toggleButton.style.backgroundColor = '#555';
        toggleButton.style.color = 'white';
        toggleButton.style.cursor = 'pointer';
        
        controlBar.appendChild(statusContainer);
        controlBar.appendChild(toggleButton);
        document.body.appendChild(controlBar);

        window.surfariMode = false;

        const updateUI = (enabled) => {{
            toggleButton.textContent = enabled ? 'Switch to Manual' : 'Continue to Automation';
            controlBar.style.backgroundColor = enabled ? 'lightgreen' : 'gold';
        }};

        toggleButton.onclick = () => {{
            window.surfariMode = !window.surfariMode;
            updateUI(window.surfariMode);
        }};

        document.addEventListener('submit', (e) => {{
            if (!window.surfariMode) {{
                window.surfariMode = true;
                updateUI(true);
            }}
        }}, true);

        updateUI(window.surfariMode);
    }})();
    """
    await page.evaluate(js_code)

async def remove_control_bar(page):
    await page.evaluate("""
        const bar = document.getElementById("surfari-control-bar");
        if (bar) bar.remove();
    """)


