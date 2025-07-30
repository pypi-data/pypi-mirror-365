import asyncio
import nest_asyncio
import json
import traceback
from typing import Dict, Any


import surfari.structured_llm as llm
import surfari.db_service as db_service
import surfari.config as config
from surfari.intelligent_masker import IntelligentMasker
from surfari.site_credential_manager import SiteCredentialManager

import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)

class BaseTool:
    def __init__(
        self,
        model=None,
        site_id=None,
        name=None,
        mask_sensitive_info=True,
    ):
        self.name = name if name else "BaseTool"
        if model is None:
            llm_model_key = f"llm_model_{self.name}"
            llm_model = config.CONFIG["app"].get(llm_model_key)
            if not llm_model:
                llm_model = config.CONFIG["app"]["llm_model"]             
            model = llm_model
        self.model = model
        # Create a single AmountReplacer instance for reuse
        if mask_sensitive_info:
            self.mask_sensitive_info = True
            self.sensitive_handler = IntelligentMasker()
        else:
            self.mask_sensitive_info = False
            self.sensitive_handler = None
        self.site_id = site_id if site_id else 0
        self.chat_history = []
        
    @classmethod
    def replace_placeholder_with_secret(cls, site_id, place_holder):
        """
        Replace any substring in `place_holder` that matches a secret_dict key with its corresponding value.
        Example: if place_holder = "{PasswordAssistant}" and dict has "PasswordAssistant": "pass123", return "{pass123}".
        """
        logger.debug(f"Getting secret for site_id={site_id}, place_holder={place_holder}")

        # Lazy load the secret_dict
        secret_dict = getattr(cls, "secret_dict", None)
        if secret_dict is None:
            logger.debug("Loading secrets from database")
            nest_asyncio.apply()
            secret_dict = asyncio.get_event_loop().run_until_complete(cls._load_secrets_from_db())
            setattr(cls, "secret_dict", secret_dict)

        site_secrets = secret_dict.get(site_id, {})
        for secret_key, secret_value in site_secrets.items():
            if secret_key in place_holder:
                replaced_key = place_holder.replace(secret_key, secret_value)
                logger.debug(f"Replaced '{secret_key}' with #### in '{place_holder}'")
                return replaced_key

        logger.debug(f"No matching partial key found in '{place_holder}'")
        return place_holder  # Return original key if no match found


    @classmethod
    async def _load_secrets_from_db(cls):
        """
        Load secrets from the database and return a dictionary.
        """
        enc = SiteCredentialManager()
        secrets = enc.load_all_secrets()
        return secrets
         
    def always_hide_secret(self, text:str) -> str:
        username = self.replace_placeholder_with_secret(self.site_id, "UsernameAssistant")
        password = self.replace_placeholder_with_secret(self.site_id, "PasswordAssistant")
        if username:
            text = text.replace(str(username), str("UsernameNotShown"))
        if password:
            text = text.replace(str(password), str("PasswordNotShown"))
        return text
    
    def add_donot_mask_terms_from_string(self, in_string: str):
        """
        Tokenize the in_string and add digit-containing tokens to terms that shouldn't be masked.
        """
        if not self.sensitive_handler:
            return
        
        self.sensitive_handler.add_donot_mask_terms_from_string(in_string)
    
    def do_mask_sensitive_info(self, text: str, donot_mask=[]):
        """Proxy to sensitive_handler.mask_sensitive_info."""
        if not self.sensitive_handler:
            return text
        return self.sensitive_handler.mask_sensitive_info(text, donot_mask=donot_mask)

    def recover_sensitive_info(self, modified_text: str):
        """Proxy to sensitive_handler.recover_sensitive_info."""
        secret_val = self.replace_placeholder_with_secret(self.site_id, modified_text)
        if secret_val:
            return secret_val

        if not self.sensitive_handler:
            return modified_text
        return self.sensitive_handler.recover_sensitive_info(modified_text)
    
    def recover_sensitive_info_in_json(self, json_obj):
        """
        Recursively processes a JSON object to recover and normalize numbers in:
        - String values (e.g., "twenty five" → "25")
        - Numeric values (e.g., 25.0 → "25" or 25.5 → "25.5")
        
        Args:
            json_obj: Input JSON (dict, list, or primitive)
            
        Returns:
            A new object with numbers recovered and normalized in strings/numbers.
        """
        if isinstance(json_obj, dict):
            new_obj = {}
            for key, value in json_obj.items():
                if key == "value":
                    new_obj["orig_value"] = value  # Save the original value first
                if key == "target":
                    new_obj["orig_target"] = value  # Save the original target first
                new_obj[key] = self.recover_sensitive_info_in_json(value)
            return new_obj            
        elif isinstance(json_obj, list):
            return [self.recover_sensitive_info_in_json(item) for item in json_obj]
        elif isinstance(json_obj, str):
            return self.recover_sensitive_info(json_obj)  # Process text (e.g., "one" → "1")
        elif isinstance(json_obj, (int, float)):
            # Normalize numbers (e.g., 25.0 → "25", 25.5 → "25.5")
            return str(int(json_obj)) if json_obj == int(json_obj) else str(json_obj)
        else:
            return json_obj  # Leave booleans/None unchanged
    
                  
    async def llm_tool_call(self, question, tools, image_data=None, execution_context=None):
        
        tool_calls = llm.structured_invoke(
            question,
            tools=tools,
            model=self.model,
            image_data=image_data,
        )
        logger.trace(f"Got Tool calls: {tool_calls}")
        
        try:
            for tool_call in tool_calls:
                arguments = tool_call.get("arguments")

                if isinstance(arguments, dict):
                    for arg_key, arg_value in arguments.items():
                        data_list = arg_value  # expected to be a list of dicts

                        if isinstance(data_list, list):
                            for i, data_item in enumerate(data_list):
                                if isinstance(data_item, dict):
                                    for field_key, field_value in data_item.items():
                                        processed_value = self.process_tool_call_data(field_value)
                                        logger.trace(f"Processed value for key {field_key}: {processed_value}")
                                        data_item[field_key] = processed_value  # update in place

                                    # Optionally process the entire dict (row-level logic)
                                    self.process_tool_call_row(data_item)
                                else:
                                    logger.debug(f"List item is not a dictionary: {data_item}")
                                    processed_item = self.process_tool_call_data(data_item)
                                    data_list[i] = processed_item  # update list in-place
                        else:
                            logger.debug(f"Expected a list under key '{arg_key}', got: {type(data_list).__name__}")
                else:
                    logger.warning(f"'arguments' is not a dict: {type(arguments).__name__} -> {arguments}")

                logger.debug(f"Calling tool: {tool_call.get('name')}")
                logger.trace(json.dumps(arguments, indent=2))

                for tool in tools:
                    if tool.__name__ == tool_call.get("name"):
                        if execution_context:
                            result = await tool(**arguments, execution_context=execution_context)
                        else:
                            result = await tool(**arguments)
                        tool_call["result"] = result
                        logger.debug(f"Result of {tool.__name__}: {result}")
                        break
                logger.debug(f"Tool call complete: {tool_call}")
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            logger.error(traceback.format_exc())
        
        return tool_calls   
    
    def process_tool_call_data(self, data):
        return data
    
    def process_tool_call_row(self, row):
        return row
    
    def get_llm_stats(self) -> Dict[str, Any]:
        return llm.token_stats.get_token_stats()
    
    async def insert_run_stats(self):
        """Insert LLM stats into the database"""
        llm_stats = self.get_llm_stats()        
            
        model = config.CONFIG["app"]["llm_model"]
        model_input_cost = config.CONFIG["app"]["model_costs"]["input"]
        model_output_cost = config.CONFIG["app"]["model_costs"]["output"]

        # for each key in llm_stats, insert the value into the database
        with db_service.get_db_connection_sync() as conn:
            c = conn.cursor()        
            for tool_name, stats in llm_stats.items():
                prompt_token_count = stats.get("prompt_token_count", 0)
                candidates_token_count = stats.get("candidates_token_count", 0)
                prompt_token_cost = prompt_token_count * model_input_cost / 1_000_000.00
                candidates_token_cost = candidates_token_count * model_output_cost / 1_000_000.00
                total_llm_cost = prompt_token_cost + candidates_token_cost
                stats["prompt_token_cost"] = float(f"{prompt_token_cost:.3f}")
                stats["candidates_token_cost"] = float(f"{candidates_token_cost:.3f}")
                stats["total_llm_cost"] = float(f"{total_llm_cost:.3f}")
                logger.debug(f"Inserting stats for : {tool_name}, Stats: {json.dumps(stats, indent=2)}")
                
                # Insert the stats into the database
                c.execute("""INSERT INTO planner_run_stats (model, tool_name, prompt_token_count, candidates_token_count, prompt_token_cost, candidates_token_cost, total_llm_cost) 
                    VALUES (:model, :tool_name, :prompt_token_count, :candidates_token_count, :prompt_token_cost, :candidates_token_cost, :total_llm_cost)""",
                    {
                    "model": model,
                    "tool_name": tool_name,
                    "prompt_token_count": prompt_token_count,
                    "candidates_token_count": candidates_token_count,
                    "prompt_token_cost": prompt_token_cost,
                    "candidates_token_cost": candidates_token_cost,
                    "total_llm_cost": total_llm_cost
                    })
                    
            conn.commit()
            conn.close()    
    
            
                
                