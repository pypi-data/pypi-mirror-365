import time
from typing import Tuple
import re
import json
import os
import difflib
from playwright.async_api import Locator

import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)

class WebPageTextExtractor:
    TEXT_LINE_PATTERN = re.compile(r"^(?P<frame_name>[^\s]+)\s+(?P<content>.*?)\s*\((?P<coords>x=[-\d\.]+,\s*y=[-\d\.]+,\s*w=[\d\.]+,\s*h=[\d\.]+),\s*xpath=(?P<xpath>.*?)\)$")
    BRACKET_DIGIT_FIX = re.compile(r'(\[+|\{+)([^\d\[\]\{\}]{3,})(\d+)(\]+|\}+)(?!\d)')
    BRACKET_BUTTON_FIX = re.compile(r'\[(↑|↓|←|→|B|E|X|IMG)(\d+)\](?!\d)')

    ICON_RE = re.compile(r"([^\[\{]*?)([☐✅🔘🟢]\d*)([^\]\}]*?)")
    BRACKET_RE = re.compile(r"^((\[{1,2}[^\[\]\{\}]+]{1,2}|\{{1,2}[^\[\]\{\}]+}{1,2})\d*)$")
    BRACKETED_PREFIX_PATTERN = re.compile(r'^((\[{1,2}[^\[\]]+\]{1,2}|\{{1,2}[^\{\}]+\}{1,2})\d*)')


    WHITESPACE_RE = re.compile(r'\s+')
    
    def __init__(self):
        self.locator_map = {}
        self.original_text_mapping = {}
        self.duplicate_text_mapping = {}

    # =============================================================================
    # Helper functions for extraction.
    # =============================================================================
    async def extract_text_from_frame(
        self,
        frame,
        depth=0,
        parent_x=0,
        parent_y=0,
        parent_xpath="",
    ):
        """
        Recursively extracts text from this `frame` (or iframe), adjusting coordinates
        based on the iframe's offset. Also prefixes `xpath` with the parent's path if provided.
        Also handles <input> <select> elements.
        """
        try:
            # Define the complete extraction script with ancestor checking
            js_path_min = os.path.join(os.path.dirname(__file__), "html_to_text.min.js")
            js_path_normal = os.path.join(os.path.dirname(__file__), "html_to_text.js")
            if os.path.exists(js_path_min) and os.path.exists(js_path_normal):
                if os.path.getmtime(js_path_min) > os.path.getmtime(js_path_normal):
                    js_path = js_path_min
                else:
                    js_path = js_path_normal
            else:
                js_path = js_path_min if os.path.exists(js_path_min) else js_path_normal
                
            logger.debug(f"Using JS path: {js_path}")
                
            with open(js_path, "r", encoding="utf-8") as f:
                common_script = f.read()            
                
            extraction_script = rf"""
                (isInSideIframe = false) => {{
                    {common_script}
                    return segments;                        
                }}
            """
            prefix = "main_frame"
            is_inside_iframe = False
            if depth > 0:
                is_inside_iframe = True
                frame_element = await frame.frame_element()
                prefix_val = await frame_element.get_attribute("id")
                if not prefix_val:
                    prefix_val = await frame_element.get_attribute("name")
                prefix = prefix_val if prefix_val else "nested_frame"
                logger.debug(f"inside of frame, prefix is now {prefix}")

            if prefix == "nested_frame":
                return "", {}
            
            segments = await frame.evaluate(extraction_script, is_inside_iframe)
            pieces = []
            legend_dict = {}
            for seg in segments:
                seg_type = seg["type"]

                if seg_type == "text" or seg_type == "input":
                    # Adjust coordinates relative to parent iframe
                    adjusted_x = seg["x"] + parent_x
                    adjusted_y = seg["y"] + parent_y

                    # Combine xpath with parent if needed
                    combined_xpath = seg["xpath"]
                    if parent_xpath:
                        combined_xpath = parent_xpath.rstrip("/") + seg["xpath"]

                    # If this text node or an ancestor is clickable, enclose in [  ]
                    num_of_brackets = seg.get("enclose", 0)
                    logger.trace(f"Checking interactive level and number of brackets to add for {seg['content']} is {num_of_brackets}")
                    
                    if num_of_brackets == 0:
                        text_content = seg["content"]
                    elif num_of_brackets == 2:
                        text_content = f"[[{seg['content']}]]"         
                    else: text_content = f"[{seg['content']}]"

                    labelText = seg.get("labelText", None)
                    if labelText:
                        logger.trace(f"Adding labelText to legend_dict for {seg['content']}: {labelText}")
                        # add xpath:lableText to legend_dict
                        legend_dict[combined_xpath] = labelText if len(labelText) <= 80 else labelText[:80] + "..."
                        
                    pieces.append(
                        f"{prefix} {text_content} "
                        f"(x={adjusted_x:.2f}, y={adjusted_y:.2f}, "
                        f"w={seg['width']:.2f}, h={seg['height']:.2f}, xpath={combined_xpath})"
                    )

                elif seg_type == "iframe":
                    frame_id = seg["id"]
                    adjusted_iframe_x = seg["x"] + parent_x
                    adjusted_iframe_y = seg["y"] + parent_y
                    iframe_coord = f"(x={adjusted_iframe_x:.2f}, y={adjusted_iframe_y:.2f}, w={seg['width']:.2f}, h={seg['height']:.2f})"

                    # Build combined iframe xpath
                    combined_iframe_xpath = seg["xpath"]
                    if parent_xpath:
                        combined_iframe_xpath = parent_xpath.rstrip("/") + seg["xpath"]

                    iframe_handle = await frame.query_selector(f'iframe[data-frame-id="{frame_id}"]')
                    if iframe_handle:
                        nested_frame = await iframe_handle.content_frame()
                        if nested_frame:
                            logger.info(
                                f"Getting text from nested iframe {frame_id} "
                                f"(depth={depth + 1}, url={nested_frame.url}"
                            )
                            nested_text, iframe_legend_dict = await self.extract_text_from_frame(
                                nested_frame,
                                depth + 1,
                                adjusted_iframe_x,
                                adjusted_iframe_y,
                                parent_xpath=combined_iframe_xpath,
                            )
                            pieces.append(nested_text)
                            # merge legend_dicts
                            for k, v in iframe_legend_dict.items():
                                if k not in legend_dict:
                                    legend_dict[k] = v
                                else:
                                    logger.warning(f"Duplicate legend entry for {k}: {legend_dict[k]} and {v}")
                            
            return "\n".join(pieces), legend_dict
        except Exception as e:
            logger.error(f"Error extracting text from frame: {e}")
            return "", {}
      
    def _reset(self):
        """
        Resets the locator map and text mappings.
        """
        self.locator_map.clear()
        self.original_text_mapping.clear()
        self.duplicate_text_mapping.clear()
      
    async def get_full_text(self, page, lazy_build_locator=True):
        """
        Extracts text from the main frame and all nested iframes, returning
        lines with coordinates + xpaths (including prefixed iframe paths).
        Encloses text in [  ] if the element is clickable.

        Also includes special rendering for <input> and <select> elements
        """
        start = time.time()
        logger.debug("Extracting text from page...")
        self._reset()
        full_text, legend_dict = await self.extract_text_from_frame(page, parent_xpath="")
        full_text, new_legend_dict = self.process_duplicate_content(full_text, legend_dict=legend_dict)
        self.create_content_map(full_text)
        
        if not lazy_build_locator:
            logger.debug("Building locators from extracted full text...")
            await self.create_locator_from_text(page, full_text)
            logger.debug("Finished building locators from extracted full text...")

            
        end = time.time()
        new_legend_dict = dict(sorted(new_legend_dict.items()))
        logger.debug(f"Final legend dict contents ({len(new_legend_dict)} items): {json.dumps(new_legend_dict, indent=2)}")        
        logger.info(f"Extracted text in {end - start:.2f} seconds:")        
        return full_text, new_legend_dict

    def create_content_map(self, text):
        """
        Creates a mapping of content to original lines.
        Content is defined as the text between the first space and '(x='.
        
        Args:
            text (str): Input text with lines containing coordinates
        
        Returns:
            dict: {content: original_line} mapping
        """
        logger.debug("Creating text content map from extracted text...")
                
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                logger.warning(f"Skipping empty line: {line}")
                continue
                
            match_obj =  self.TEXT_LINE_PATTERN.match(line)
            if not match_obj:
                logger.warning(f"Skipping line without expected pattern: {line}")
                continue
            
            content = match_obj.group("content").strip()
            content = self._escape_quotes(content)
            content, __ = self._process_select_option_content(content)   
            self.original_text_mapping[content] = line
            
        logger.debug(f"Added {len(self.original_text_mapping)} lines to the text content map")
    
    def find_best_fuzzy_match(self, noisy_key, key_map, min_similarity=0.8):
        """
        Finds the best matching key in key_map for a noisy input,
        only considering keys with matching bracket type.
        """
        input_match = self.BRACKET_RE.match(noisy_key)
        if not input_match:
            return None  # reject malformed input

        bracket_type = noisy_key[0]  # '[' or '{'
        normalized_input = input_match.group(1).strip()

        best_match = None
        best_score = 0.0

        for candidate in key_map.keys():
            candidate_match = self.BRACKET_RE.match(candidate)
            if not candidate_match:
                continue  # skip malformed or non-bracketed keys

            candidate_bracket_type = candidate[0]
            if bracket_type != candidate_bracket_type:
                continue  # enforce strict bracket type match

            normalized_candidate = candidate_match.group(1).strip()

            score = difflib.SequenceMatcher(None, normalized_input, normalized_candidate).ratio()
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= min_similarity:
            return best_match
        return None
    
    async def get_locator_from_text(self, page, text) -> Tuple[Locator, bool]:
        """
        Extracts locator information from the provided text.
        """
        logger.sensitive(f"Getting locator from text parameter: {text}")
        text = re.sub(r'[^\S\r\n]+', ' ', text)
        is_expandable_element = False
        match = self.ICON_RE.match(text) 
        if match:
            text = match.group(2)
            logger.debug(f"Found icon match, using text: {text}")
        else:
            match = self.BRACKET_RE.match(text)
            if match:
                text = match.group(1)
                logger.sensitive(f"Found bracket match, using text: {text}")
            else:
                match = self.BRACKETED_PREFIX_PATTERN.match(text)
                if match:
                    text = match.group(1)
                    logger.debug(f"Found bracketed prefix match, using text: {text}")
                else:
                    return None, is_expandable_element
        # when we get here, we have a valid text that is either an radio/checkbox icon or a bracketed text optionally with a number   
        orig_text = self._escape_quotes(text.strip())
        locator   = self.locator_map.get(orig_text)
        if locator:
            is_expandable_element = orig_text.startswith("[[") or orig_text.startswith("[E]")
            return locator, is_expandable_element
        
        text = orig_text
        text_info_line = self.original_text_mapping.get(orig_text)
        # will try to fix line breaks emclosed in brackets or misplaced index numbers (inside brackets)
        if not text_info_line:
            logger.warning(f"Key still not found. Trying to fix line breaks or misplaced index numbers for: {orig_text}")
            TRANSFORMS = [
                ("newline→space", lambda s: self.WHITESPACE_RE.sub(" ", s.replace("\n", " ")).strip()),
                ("newline→empty", lambda s: self.WHITESPACE_RE.sub(" ", s.replace("\n", "")).strip()),
            ]
            if "[" in orig_text or "{" in orig_text:
                TRANSFORMS.append(
                    ("bracket-digit fix",
                    lambda s: self.BRACKET_DIGIT_FIX.sub(
                        lambda m: f"{m[1]}{m[2]}{m[4]}{m[3]}", s))
                )
                TRANSFORMS.append(
                    ("bracket-button fix",
                    lambda s: self.BRACKET_BUTTON_FIX.sub(
                        lambda m: f"[{m[1]}]{m[2]}", s))
                )
            for label, transform in TRANSFORMS:
                candidate = transform(orig_text)
                if candidate != orig_text:
                    logger.warning(f"[fallback:{label}] trying key: {candidate!r}")
                    text_info_line = self.original_text_mapping.get(candidate)
                    if text_info_line:
                        text = candidate
                        break
        
        if not text_info_line:
            logger.warning(f"Key still not found. Trying to match with fussy matching for: {orig_text}")            
            best_match = self.find_best_fuzzy_match(orig_text, self.original_text_mapping)
            if best_match:
                text_info_line = self.original_text_mapping.get(best_match)
                text = best_match
                logger.warning(f"Fuzzy match found: {text} for {orig_text}")

        if text_info_line: # lazy locator creation case       
            await self.create_locator_from_text(page, text_info_line)
        locator = self.locator_map.get(text, None)
                    
        # LLM returned some text that is not in the original text unit (line)     
        # We did not find the locator in the maps, so we try to get it from the page                    
        if not locator:
            # LLM passed back some text that is not in the original text unit (line)
            logger.warning(f"Didn't find text in the original text unit line: {text}, giving up...")                             
        else:
            is_expandable_element = text.startswith("[[") or text.startswith("[E]")
        return locator, is_expandable_element
    
    def is_included_to_duplicate(self, content):
        # non-interactable elements should be excluded from de-dup
        if ((content.startswith(("[", "{")) and content.endswith(("]", "}"))) 
            or content in ("☐", "✅", "🔘", "🟢")):
            return True
        return False

    def process_duplicate_content(self, text, legend_dict=None):
        logger.debug("Processing duplicate text content...")  
        content_count = {}
        modified_lines = []
        new_legend_dict = {}

        # First pass: count occurrences of each non-protected content                
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
                
            match_obj =  self.TEXT_LINE_PATTERN.match(line)
            if not match_obj:
                logger.warning(f"Skipping line without expected pattern: {line}")
                continue
                
            content = match_obj.group("content").strip()  
            content, __ = self._process_select_option_content(content)      
            if self.is_included_to_duplicate(content):
                content_count[content] = content_count.get(content, 0) + 1
        
        # Second pass: modify all duplicates and build mapping
        content_occurrences = {}
        number_of_duplicates = 0
        
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
                
            match_obj =  self.TEXT_LINE_PATTERN.match(line)
            if not match_obj:
                logger.warning(f"Skipping line without expected pattern: {line}")
                continue
                
            content = match_obj.group("content").strip()   
            content, remainder = self._process_select_option_content(content)
            if remainder:
                remainder = f"|| {remainder}"      
            
            frame_name = match_obj.group("frame_name").strip() 
            coords = match_obj.group("coords").strip()
            xpath = match_obj.group("xpath").strip()
            
            labelText = None
            if legend_dict:
                labelText = legend_dict.get(xpath, None)

            if content_count.get(content, 0) > 1:
                number_of_duplicates += 1
                content_occurrences[content] = content_occurrences.get(content, 0) + 1
                occurence_index = content_occurrences[content]
                new_content = f'{content}{occurence_index}{remainder}'
                modified_line = f"{frame_name} {new_content} ({coords}, xpath={xpath})"
                self.duplicate_text_mapping[new_content] = modified_line
                modified_lines.append(modified_line)
                if labelText:
                    new_legend_dict[f"{new_content}"] = labelText
            else:
                modified_lines.append(line)
                if labelText:
                    new_legend_dict[f"{content}"] = labelText
        
        logger.debug(f"Processed {number_of_duplicates} duplicate text content...")        
        return '\n'.join(modified_lines), new_legend_dict

    def truncate_xpath_to_interactive(self, full_xpath):
        segments = [seg for seg in full_xpath.split('/') if seg.strip()]
        last_interactive = -1
        for i in range(len(segments) - 1, -1, -1):
            if segments[i].startswith(('a[', 'button')) or segments[i] == 'a':
                last_interactive = i
                break
        if last_interactive == -1:
            return full_xpath
        return '/' + '/'.join(segments[:last_interactive + 1])


    def chain_locators_from_strings(self, host_locator, locator_str):
        current_locator = host_locator
        locator_str = locator_str.strip()
        if locator_str.startswith("locator("):
            # Handle page.locator() or locator.locator()
            selector = locator_str[len("locator("):-1].strip()
            if selector.startswith(("'", '"')) and selector.endswith(("'", '"')):
                # Remove quotes from the selector string
                selector = selector[1:-1]
            current_locator = current_locator.locator(selector)
        elif locator_str.startswith("get_by_role("):
            match = re.match(r"get_by_role\('([^']+)'(?:,\s*name='([^']+)')?\)", locator_str)
            if match:
                role = match.group(1)
                name = match.group(2)
                current_locator = current_locator.get_by_role(role, name=name)
            else:
                raise ValueError(f"Unrecognized get_by_role format: {locator_str}")
        elif locator_str.startswith("get_by_label("):
            match = re.match(r"get_by_label\('([^']+)'\)", locator_str)
            if match:
                label = match.group(1)
                current_locator = current_locator.get_by_label(label)
            else:
                raise ValueError(f"Unrecognized get_by_label format: {locator_str}")
        else:
            # If the string doesn't match a known locator method
            raise ValueError(f"Unrecognized locator string format: {locator_str}")
        return current_locator


    def locate_element_with_xpath(self, page, xpath):
        """
        Locates an element using the given XPath, handling iframe boundaries if present.
        Uses `page.frame_locator` for iframe handling.
        """
        xpath = self.truncate_xpath_to_interactive(xpath)
        if '/iframe' in xpath:
            iframe_xpath, remaining_xpath = xpath.split('/iframe[', 1)
            iframe_xpath += '/iframe[' + remaining_xpath.split(']', 1)[0] + ']'
            remaining_xpath = remaining_xpath.split(']', 1)[1]
            frame_loc = page.frame_locator(f'xpath={iframe_xpath}')
            element = frame_loc.locator(f'xpath={remaining_xpath}')
        elif '/#shadow-root/' in xpath:
            shadow_root_xpath, remaining_xpath = xpath.split('/#shadow-root/', 1)
            host_node_locator = page.locator(f'xpath={shadow_root_xpath}')
            element = self.chain_locators_from_strings(host_node_locator, remaining_xpath)
        else:
            element = page.locator(f'xpath={xpath}')
        return element

    @staticmethod
    def _escape_quotes(text: str) -> str:
        """Escape only " and ' in a string (for Playwright's has_text)"""
        return text.replace('"', r'\"').replace("'", r"\'")
          
    async def create_locator_from_text(self, page, text):
        """
        Parses the generated full text and creates Playwright locators for each element.
        
        For lines starting with:
        - "main_frame": creates locator using page.get_by_role()
        - frame names: creates locator using page.frame_locator().get_by_role()
        
        The role is determined by:
        - "link" if xpath contains "a" and text is enclosed in []
        - "button" if text is enclosed in []
        - Appropriate input locators based on input type
        """       
        added_count = 0
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
                
            match_obj =  self.TEXT_LINE_PATTERN.match(line)
            if not match_obj:
                logger.warning(f"Skipping line without expected pattern: {line}")
                continue
                
            content = match_obj.group("content").strip()
            content = self._escape_quotes(content)
            content, __ = self._process_select_option_content(content)   
                     
            frame_name = match_obj.group("frame_name").strip()
            is_main_frame = (frame_name == "main_frame")
            frame_loc = page.frame_locator(f'iframe[id="{frame_name}"], iframe[name="{frame_name}"]')
            
            xpath = match_obj.group("xpath").strip()            
            need_to_use_xpath = False
            
            locator = None            
            # checkboxes and radio buttons and empty content/icon size buttons
            if content.startswith(("☐", "🔘", "✅", "🟢", "[↑]", "[↓]", "[←]", "[→]", "[B]", "[E]", "[X]", "[IMG]")):
                logger.debug(f"Will create checkbox/radio/empty content/icon size locator from xpath: {content}")
                need_to_use_xpath = True
                
            # clickable elements    
            elif content.startswith("[") and content.endswith("]"):
                text_val = content[1:-1]
                # nested brackets
                if text_val.startswith("[") and text_val.endswith("]"):
                    text_val = text_val[1:-1] 
                
                if "/a[" in xpath.lower():
                    role = "link"
                    tag = "a"
                elif "/button[" in xpath.lower():
                    role = "button"
                    tag = "button"
                else:
                    role = "menuitem"
                    tag = "div"
                if is_main_frame:
                    locator = page.get_by_role(role, name=text_val, exact=True)
                    if await locator.count() == 0:
                        locator = page.get_by_role(role).filter(has_text=re.compile(rf'^{re.escape(text_val)}$'))
                        if await locator.count() == 0:
                            locator = page.locator(f'{tag}:has-text("{text_val}")')
                else:
                    locator = frame_loc.get_by_role(role, name=text_val, exact=True)
                    if await locator.count() == 0:
                        locator = frame_loc.get_by_role(role).filter(has_text=re.compile(rf'^{re.escape(text_val)}$'))
                        if await locator.count() == 0:
                            locator = frame_loc.locator(f'{tag}:has-text("{text_val}")')
                        
            # select options            
            elif content.startswith("{{") and content.endswith("}}"):
                text_val = content[2:-2]
                if is_main_frame:
                    locator = page.get_by_role('combobox').filter(has=page.get_by_role('option', name=text_val, exact=True))
                    if await locator.count() == 0:
                        locator = page.locator('select').filter(has=page.locator('option', has_text=text_val))
                else:
                    locator = frame_loc.get_by_role('combobox').filter(has=frame_loc.get_by_role('option', name=text_val, exact=True))
                    if await locator.count() == 0:
                        locator = frame_loc.locator('select').filter(has=frame_loc.locator('option', has_text=text_val))                    
            # input text
            elif content.startswith("{") and content.endswith("}"):
                text_val = content[1:-1]
                if is_main_frame:
                    locator = page.get_by_role("textbox", name=text_val, exact=True)
                    if await locator.count() == 0:
                        locator = page.get_by_role("searchbox", name=text_val, exact=True)
                        if await locator.count() == 0:
                            locator = page.get_by_role("combobox", name=text_val, exact=True)
                            if await locator.count() == 0:
                                locator = page.get_by_role("spinbutton", name=text_val, exact=True)    
                                if await locator.count() == 0:
                                    locator = page.locator(f'input[name="{text_val}"]')                      
                else:
                    locator = frame_loc.get_by_role("textbox", name=text_val, exact=True)
                    if await locator.count() == 0:
                        locator = frame_loc.get_by_role("searchbox", name=text_val, exact=True)
                        if await locator.count() == 0:
                            locator = frame_loc.get_by_role("combobox", name=text_val, exact=True)
                            if await locator.count() == 0:
                                locator = frame_loc.get_by_role("spinbutton", name=text_val, exact=True)       
                                if await locator.count() == 0:
                                    locator = frame_loc.locator(f'input[name="{text_val}"]')                     
            if locator:
                final_count = await locator.count()
                if final_count > 1:
                    logger.sensitive(f"For content: {content}, will use xpath because locator resolved to {final_count} elements: {locator}")
                    need_to_use_xpath = True
                elif final_count == 0:
                    logger.sensitive(f"For content: {content}, will use xpath because locator not resolved to any elements: {locator}")
                    need_to_use_xpath = True
                else:
                    logger.sensitive(f"Locator for {content} resolved to {final_count} elements: {locator}")
            elif not need_to_use_xpath: # catch balanced brackets that were not processed or duplicate contents
                if re.fullmatch(r"^(\[\[.*\]\]|\{\{.*\}\}|\[.*\]|\{.*\})\d*$", content):
                    logger.debug(f"For content: {content}, will use xpath becasue locator was not created yet")
                    logger.trace(f"trying to create from xpath: {xpath}")
                    need_to_use_xpath = True
                
            if need_to_use_xpath:
                locator = self.locate_element_with_xpath(page, xpath)
                
            if locator:
                self.locator_map[content] = locator
                logger.trace(f"Locator for {content} (mapped by xpath) added to map: {locator}")
                added_count += 1
                
        logger.debug(f"Created {added_count} locators from text content, total locators in map: {len(self.locator_map)}")

    def _process_select_option_content(self, content):
        """
        Returns a tuple:

            (first_segment, second_segment)

        where *first_segment* is the text **before** the first "||"
        (normalised to {{…}} when needed) and *second_segment* is the text
        **immediately after** that first "||" (trimmed of whitespace).

        If there is no "||" in *content*, the entire string is returned as
        the first element and the second element is an empty string.
        """
        if "||" not in content:
            return content.strip(), ""

        first, remainder = [s.strip() for s in content.split("||", 1)]

        # normalise first segment if it looks like {{ … }}
        if first.startswith("{{") and first.endswith("}}"):
            inner = first[2:-2].strip()
            first = f"{{{{{inner}}}}}"

        return first, remainder

    def filter_legend(self, legend_dict):
        COMMON_DIRECTIONAL_WORDS = {"previous", "next", "up", "down", "back", "forward"}
        
        # Filter out entries where value is a common directional word (case-insensitive)
        filtered = {
            k: v for k, v in legend_dict.items()
            if v.lower() not in COMMON_DIRECTIONAL_WORDS
        }
        legend_str = "\n".join([f"{k} {v}" for k, v in filtered.items()])
        instruction = "=" * 80 + "\n"
        instruction += "Legend Area for Small Buttons. Don't React within this Region\n"
        legend_str = instruction + legend_str
        legend_str += "\nEnd Legend Area for Small Buttons. Don't React within this Region\n"        
        legend_str += "=" * 80 + "\n"
        return legend_str

    def get_duplicate_texts(self):
        """
        return only the keys of the duplicate_text_mapping as a list
        """
        return list(self.duplicate_text_mapping.keys())
            