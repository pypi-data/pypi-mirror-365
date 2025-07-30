
import json
import re, copy
import time
import os
import asyncio
import traceback
from playwright.async_api import Error

import surfari.config as config
import surfari.surfari_logger as surfari_logger
import surfari.playwright_util as playwright_util
import surfari.text_layouter as text_layouter
import surfari.structured_llm as llm_service
from surfari.gmail_otp_fetcher import GmailOTPClientAsync
from surfari.site_credential_manager import SiteCredentialManager
from surfari.full_text_extractor import WebPageTextExtractor
from surfari.tools import BaseTool
from surfari.tools.navigation_tool._prompts import NAVIGATION_TOOL_SYSTEM_PROMPT, NAVIGATION_USER_PROMPT, SINGLE_ACTION_EXAMPLE, MULTI_ACTION_EXAMPLE, STEP_EXECUTION_SINGLE, STEP_EXECUTION_SEQUENCE

logger = surfari_logger.getLogger(__name__)

class NavigationTool(BaseTool):
    def __init__(
        self,
        model=None,
        site_id=None,
        site_name=None,
        url=None,
        name=None,
        mask_sensitive_info=True,
        multi_action_per_turn=False,
    ):
        name = name if name else "NavigationTool"
        # look up by site_name fuzzy match
        if site_name:
            scm = SiteCredentialManager()
            site_info = scm.find_site_info_by_name(site_name)
            if site_info:
                url = site_info.get("url")
                site_id = site_info.get("site_id")
        
        if not url:
            url = "https://www.google.com"
        
        self.url = url
        
        if not site_id:
            site_id = 9999
            
        self.web_page_text_extractor = WebPageTextExtractor()
        self.multi_action_per_turn = multi_action_per_turn

        super().__init__(model=model, site_id=site_id, name=name, mask_sensitive_info=mask_sensitive_info)

    async def setup_download_listener(self, page):
        async def handle_download(download):
            print(f"Download started: {download.suggested_filename}")
            # Wait for download to complete (path() blocks until done)
            print(f"Temporary path: {await download.path()}") 
            
            # Save to custom location
            dest_path = f"{config.download_folder_path}/{download.suggested_filename}"
            await download.save_as(dest_path)
            print(f"Download saved to: {dest_path}")

        # Attach the handler
        page.on("download", handle_download)
 
    async def navigate(self, page, task_goal="View statements and tax forms"):
        # Set up the download listener
        self.add_donot_mask_terms_from_string(task_goal)
        await page.goto(self.url, timeout=60000)
        logger.info("Setting up download listener...")
        await self.setup_download_listener(page)
        
        model_name = config.CONFIG["app"]["llm_model"]
        
        if not self.chat_history:
            self.chat_history = [{"role": "user", "content": "Task Goal: " + task_goal}]

        turns = 0
        consecutive_errors = 0
        wait_time_heuristic = config.CONFIG["app"].get("wait_time_heuristic", -1)                               
        answer = None
        max_turns = config.CONFIG["app"].get("max_number_of_turns", 35)
        
        system_prompt = NAVIGATION_TOOL_SYSTEM_PROMPT.format(presentation="textual layout")
        if self.multi_action_per_turn:            
            system_prompt = system_prompt.replace("__step_excution_example__", MULTI_ACTION_EXAMPLE)
            system_prompt = system_prompt.replace("__step_execution_single_or_sequence__", STEP_EXECUTION_SEQUENCE)
        else:
            system_prompt = system_prompt.replace("__step_excution_example__", SINGLE_ACTION_EXAMPLE)
            system_prompt = system_prompt.replace("__step_execution_single_or_sequence__", STEP_EXECUTION_SINGLE)

        try:
            while turns < max_turns:
                turns += 1
                page_layot = await self.generate_text_representation(page)
                user_prompt = NAVIGATION_USER_PROMPT.format(page_content=page_layot)

                # goal = self.chat_history[0]
                # recent = self.chat_history[-12:]
                # feedback_for_llm = [goal] + [msg for msg in recent if msg is not goal]
                feedback_for_llm = self.chat_history

                llm_response_json = await llm_service.process_prompt_return_json(system_prompt=system_prompt, 
                                                                                user_prompt=user_prompt,
                                                                                chat_history=feedback_for_llm,
                                                                                model=model_name,
                                                                                purpose=self.name, 
                                                                                site_id=self.site_id,)
                # important: do this before recovering sensitive info
                self.chat_history.append({"role": "assistant", "content": json.dumps(llm_response_json)})       
                
                llm_response_json = self.recover_sensitive_info_in_json(llm_response_json)
                    
                step_execution = llm_response_json.get("step_execution", "SEQUENCE")
                
                is_iterative = step_execution == "ITERATION"
                
                single_step = llm_response_json.get("step", None)
                if single_step:
                    if isinstance(single_step, dict):
                        steps = [single_step]
                    elif isinstance(single_step, list):
                        steps = single_step
                    else:
                        logger.warning(f"Invalid step format: {single_step}, expected dict or list.")
                        steps = []
                else:
                    steps = llm_response_json.get("steps", [])  
        
                if step_execution == "SUCCESS":
                    logger.info("SUCCESS: Task has been completed successfully.")
                    if "answer" in llm_response_json:
                        answer = llm_response_json.get("answer")
                        print(f"Final answer: {answer}")
                    break
                
                if step_execution == "BACK":
                    logger.info("BACK: Going back to the previous page.")
                    await page.go_back(timeout=60000)
                    await playwright_util.wait_for_page_load_generic(page, post_load_timeout_ms=wait_time_heuristic)
                    self.chat_history.append({"role": "user", "content": "Went back to the previous page."})
                    continue
                
                if step_execution == "WAIT":
                    logger.info("WAIT: page might still be loading.")
                    retry_wait_time = 2000
                    before_wait = time.time()
                    await playwright_util.wait_for_page_load_generic(page, post_load_timeout_ms=retry_wait_time)
                    after_wait = time.time()
                    wait_duration = after_wait - before_wait
                    self.chat_history.append({"role": "user", "content": f"I waited {wait_duration:.2f} more seconds for the page to load."})
                    continue

                if step_execution == "SCROLL":
                    logger.debug("SCROLL: to show more content.")
                    scrolled = await playwright_util.scroll_main_scrollable(page)
                    scroll_result = "SCROLL success" if scrolled else "Wait: no more content to scroll."
                    self.chat_history.append({"role": "user", "content": scroll_result})
                    await playwright_util.wait_for_page_load_generic(page, post_load_timeout_ms=wait_time_heuristic)                                       
                    continue
                       
                reasoning = llm_response_json.get("reasoning", "No reasoning provided.")
                for step in steps:
                    if "orig_value" in step and step["orig_value"] in ["UsernameAssistant", "PasswordAssistant"]:
                        # if the step has orig_value, it is a fill action
                        if step["value"] == step["orig_value"]:
                            step_execution = "DELEGATE_TO_USER"
                            reasoning = "Please manually log in."
                            break

                if step_execution == "DELEGATE_TO_USER":
                    await playwright_util.inject_control_bar(page, message=reasoning)
                    logger.info("DELEGATE_TO_USER: User action is required to continue.")
                    resumed = await self.wait_for_user_resume(page)
                    if not resumed:
                        return "Timeout waiting for user to take actions."
                    continue 
                                       
                if not steps:
                    logger.debug("No steps found in LLM response, stopping navigation.")
                    await playwright_util.wait_for_page_load_generic(page, post_load_timeout_ms=wait_time_heuristic)
                    consecutive_errors += 1
                    continue
                
                if not isinstance(steps, list):
                    logger.warning("Invalid LLM Response Format: Steps should be a list but are not.")
                    break
                
                try:
                    result, updated_steps = await self.apply_otp_to_fill_steps(steps)
                    if result > 0:
                        logger.debug(f"Applied OTP to fill {result} steps")
                        steps = updated_steps
                except Exception as e:
                    logger.exception("Error during OTP application; delegate for manual resolution.")
                    step_execution = "DELEGATE_TO_USER"
                    await playwright_util.inject_control_bar(page, message="Please clear the OTP manually.")
                    resumed = await self.wait_for_user_resume(page)
                    if not resumed:
                        return "Timeout waiting for user to take actions."
                    continue
                             
                is_locator_found = False 
                for step in steps:
                    orig_target = step.get("orig_target", "")
                    target = step.get("target", "")

                    locator, is_expandable_element = await self.get_locator_from_text(page, target)                    
                    if locator:
                        step["locator"] = locator
                        is_locator_found = True
                        if is_expandable_element:
                            logger.debug(f"Found a Locator that is expandable: {locator}, skipping the rest")
                            step["is_expandable_element"] = True
                            break
                    else:
                        if not is_locator_found:
                            if "orig_value" in step:
                                step["value"] = step["orig_value"]
                                del step["orig_value"]
                                
                            if "orig_target" in step:
                                step["target"] = step["orig_target"]
                                del step["orig_target"]  
                                                            
                            # First locator failed — hard fail
                            logger.error(f"First locator failed to resolve: {step}, informing LLM")
                            step["result"] = f"Wait: I can not interact with {orig_target}. Do you see the EXACT target in the page?"
                                                 
                            self.chat_history.append({"role": "user", "content": f"{json.dumps(step)}"})
                            consecutive_errors += 1
                            break
                        else:
                            logger.warning(f"Subsequent locator failed to resolve: {step}, skipping the rest")
                            break                  

                # Perform actions on the page after collecting all steps
                if is_locator_found:   
                    locator_actions = await playwright_util.take_actions(page, steps, num_steps=len(steps), is_iterative=is_iterative)
                    
                    for locator_action in locator_actions:
                        # remove the locator from the action
                        if "locator" in locator_action:
                            del locator_action["locator"]
                        if "orig_value" in locator_action:
                            locator_action["value"] = locator_action["orig_value"]
                            del locator_action["orig_value"]
                        elif "value" in locator_action:
                            del locator_action["value"]
                            
                        if "orig_target" in locator_action:
                            locator_action["target"] = locator_action["orig_target"]
                            del locator_action["orig_target"]
                        elif "target" in locator_action:
                            del locator_action["target"]
                            
                        if "result" in locator_action:
                            result = locator_action["result"]
                            if len(result) > 200:
                                result = result[:200] + "..."
                            locator_action["result"] = result
                            if "Error:" in result:
                                consecutive_errors += 1
                                         
                    self.chat_history.append({"role": "user", "content": f"{json.dumps(locator_actions)}"})
                    await playwright_util.wait_for_page_load_generic(page, post_load_timeout_ms=wait_time_heuristic)
            # checking backwards for the last assistant message
            last_reasoning = "No answer found."
            for i in range(len(self.chat_history) - 1, -1, -1):
                if self.chat_history[i]["role"] == "assistant":
                    assistant_content = self.chat_history[i].get("content")
                    if assistant_content:
                        assistant_content = json.loads(assistant_content)
                        last_reasoning = assistant_content.get("reasoning", "No answer found.")
                        break       
            answer = f"{str(last_reasoning)}: {str(answer)}" if answer else str(last_reasoning)
        except Exception as e:
            logger.exception("Error during navigation")
            answer = "Error occurred. Please check the logs for details."
        finally:
            logger.debug(f"Final chat history: {json.dumps(self.chat_history, indent=2)}")    
            await self.insert_run_stats() 
                   
        return answer

    async def wait_for_user_resume(self, page):
        logger.info("Delegated to human: User action is required to continue.")
        polling_times = config.CONFIG["app"].get("hil_polling_times", 60)

        while polling_times > 0:
            polling_times -= 1
            try:
                mode = await page.evaluate("window.surfariMode")
                if mode is None:
                    print("Automation mode disappeared, assuming user has taken action.")
                    return True
                if mode: 
                    print("Automation manually re-enabled by the user.")
                    await playwright_util.remove_control_bar(page)
                    return True
            except Error as e:
                if "Execution context was destroyed" in str(e):
                    print("Page navigated — assuming automation should continue.")
                    await page.wait_for_load_state("domcontentloaded")
                    return True
                else:
                    raise

            if polling_times % 10 == 0:
                logger.debug(f"Waiting for user to take actions... {polling_times} seconds left.")
            await asyncio.sleep(1)

        logger.error("Timeout waiting for user to take actions. Exiting.")
        return False


    async def apply_otp_to_fill_steps(self, steps):
        digit_steps = []
        otp_fill_indices = []

        # Step 1: Scan for both types of OTP fill targets
        for i, step in enumerate(steps):
            if step.get("action") != "fill":
                continue

            target = step.get("target", "")
            value = step.get("value")

            if value == "OTP":
                otp_fill_indices.append(i)
            else:
                match = re.fullmatch(r"\{\_(\d+)\}", target)
                if match and value == "*":
                    # This is a digit-per-box OTP field
                    digit_index = int(match.group(1))
                    digit_steps.append((digit_index, i))

        if not otp_fill_indices and not digit_steps:
            return 0, steps  # No OTP-related patterns found

        # Step 2: Fetch OTP code once
        gmail_otp_fetcher = GmailOTPClientAsync()
        otp_code = await gmail_otp_fetcher.get_otp_code()
        if not otp_code:
            logger.debug("No OTP code fetched, unable to proceed. Returning failure.")
            return 0, "failure getting otp code"

        updated_steps = copy.deepcopy(steps)
        replacements = 0

        # Step 3: Replace full OTP (value == "OTP")
        for idx in otp_fill_indices:
            updated_steps[idx]["value"] = otp_code
            replacements += 1

        # Step 4: Replace digit-per-box steps
        if digit_steps:
            digit_steps.sort()
            expected = list(range(1, len(digit_steps) + 1))
            actual = [index for index, _ in digit_steps]
            if actual != expected:
                logger.debug("Invalid OTP digit field sequence. Skipping per-digit substitution.")
            elif len(otp_code) != len(digit_steps):
                logger.debug("OTP length mismatch for digit fields. Skipping per-digit substitution.")
            else:
                for (digit_index, step_idx), digit in zip(digit_steps, otp_code):
                    step = updated_steps[step_idx]
                    if step.get("value") == "*":
                        step["value"] = digit
                        replacements += 1

        return replacements, updated_steps

    async def get_locator_from_text(self, page, text):
        """Get locator info from text."""
        return await self.web_page_text_extractor.get_locator_from_text(page, text)   

    async def generate_text_representation(self, page):
        logger.debug(f"Extracting info with text representation, site_id={self.site_id}")
        full_page_text, legend_dict = await self.web_page_text_extractor.get_full_text(page)
        if not full_page_text:
            logger.debug(f"Failed to extract text from page, site_id={self.site_id}, retrying after 5 seconds")
            await page.wait_for_timeout(5000)
            full_page_text, legend_dict = await self.web_page_text_extractor.get_full_text(page)
        await logger.log_text_to_file(self.site_id, full_page_text, self.name, "content")
        
        duplicate_texts = self.web_page_text_extractor.get_duplicate_texts()
        logger.trace(f"Duplicate texts: {duplicate_texts}")
        
        legend_str = self.web_page_text_extractor.filter_legend(legend_dict)
        
        full_page_text = text_layouter.rearrange_texts(full_page_text, additional_text=legend_str)
        logger.debug(f"always try to hide secret, site_id={self.site_id}")        
        full_page_text = self.always_hide_secret(full_page_text)
        
        await logger.log_text_to_file(self.site_id, full_page_text, self.name, "layout")
        
        # # Mask amounts with random values
        if self.mask_sensitive_info:
            full_page_text = self.do_mask_sensitive_info(full_page_text, donot_mask=duplicate_texts)
            await logger.log_text_to_file(self.site_id, full_page_text, self.name, "masked_layout")
            
        if config.CONFIG["app"].get("is_save_screenshot", False):
            await self.screenshot_page(page.context, page)                           
        return full_page_text

    async def screenshot_page(self, context, page):
        image_data_base64 = None
        # screenshot_folder = config.screenshot_folder_path        
        screenshot_time_out = config.CONFIG["app"].get("screenshot_time_out", 60)

        # Attempt screenshot if configured
        logger.debug(f"Extracting information from page with screenshot for site_id: {self.site_id}")
        current_time = time.strftime("%H:%M:%S", time.localtime())
        filename = f"site_id-{self.site_id}-{current_time}_screenshot.png"
        screenshot_file_name = os.path.join(config.debug_files_folder_path, filename)        

        try:
            await page.route("**/*.{woff,woff2,ttf,eot,otf}", lambda route: route.abort())
            screenshot = await playwright_util.capture_full_page_screenshot_via_cdp(
                context, page, screenshot_file_name, timeout=screenshot_time_out
            )
            logger.debug(f"Screenshot saved at: {screenshot_file_name}")
            image_data_base64 = screenshot["data"]
        except Exception as e:
            logger.debug(f"Screenshot error for site_id {self.site_id}: {e}")
            logger.debug(traceback.format_exc())
            
        return image_data_base64   

