import time
import json
import os
from dotenv import load_dotenv
from typing import Dict, Callable, Any, Union, List
from threading import Lock
from jsonfinder import jsonfinder
import ollama
from openai import OpenAI
from google import genai
from google.genai import types
from anthropic import Anthropic

import surfari.config as config
import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)

class TokenStats:
    def __init__(self):
        self.token_stats = {}
        self.lock = Lock()

    def update_token_stats(self, tool_name, prompt_token_count, candidates_token_count):
        with self.lock:
            if tool_name not in self.token_stats:
                self.token_stats[tool_name] = {
                    "prompt_token_count": 0,
                    "candidates_token_count": 0,
                    "total_token_count": 0,
                }
            self.token_stats[tool_name]["prompt_token_count"] += prompt_token_count
            self.token_stats[tool_name]["candidates_token_count"] += candidates_token_count
            self.token_stats[tool_name]["total_token_count"] += prompt_token_count + candidates_token_count

    def get_token_stats(self):
        with self.lock:
            return self.token_stats.copy()

token_stats = TokenStats()

load_dotenv(dotenv_path=os.path.join(config.PROJECT_ROOT, ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

def structured_invoke(
    question: str,
    tools: List[Union[Dict[str, Any], Callable[..., Any]]],
    model: str = "gpt-4o-mini",
    image_data: bytes = None,
) -> Any:
    is_open_ai = model.startswith("gpt-") or model == "o3-mini"
    is_gemini_ai = model.startswith("gemini-")
    is_anthropic = model.startswith("claude-")
    is_ollama = model.startswith("deepseek") or model.startswith("qwen") or model.startswith("llama") or model.startswith("gemma")

    if is_open_ai:
        client = OpenAI(api_key=openai_api_key)
    elif is_gemini_ai:
        client = genai.Client(api_key=gemini_api_key)
    elif is_anthropic:
        client = Anthropic(api_key=anthropic_api_key)
    elif is_ollama:
        client = ollama.Client()
    else:
        raise ValueError("Unsupported LLM Model")

    call_success = False
    tool_calls = None
    try:
        response, tool_calls = _invoke_models(client, model, tools, question, image_data=image_data)
        call_success = True
    except Exception as e:
        logger.error(f"Error invoking model: {e}")
        return []
        
    if not (tool_calls and call_success):
        logger.debug(f"The model didn't use the function. Its response was: {response}")
        logger.debug(f"Retrying once more...")
        response, tool_calls = _invoke_models(client, model, tools, question, image_data=image_data)
        logger.debug(f"Retried tool calls: {tool_calls}")
        
    return tool_calls

def _invoke_models(client, model, tools, question, image_data=None):
    logger.debug(f"Invoking model: {model} with tools: {tools}")
    is_anthropic = isinstance(client, Anthropic)

    messages = []
    if not is_anthropic and not isinstance(client, genai.Client):
        messages.append({"role": "system", "content": "You are a helpful assistant. Use tools when necessary."})

    user_message = {"role": "user", "content": question}
    if image_data:
        user_message["images"] = [image_data]
    messages.append(user_message)

    start = time.time()

    if isinstance(client, ollama.Client):
        response = client.chat(model=model, messages=messages, tools=tools)
        tool_calls = response["message"].get("tool_calls")
        response_text = response["message"].get("content")

    elif isinstance(client, OpenAI):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=tools
        )
        tool_calls = response.choices[0].message.tool_calls
        response_text = response.choices[0].message.content
        # --- Added token stats for OpenAI ---
        usage = getattr(response, "usage", None)
        if usage:
            token_stats.update_token_stats(model, getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0))

    elif isinstance(client, genai.Client):
        content = question if not image_data else [
            types.Part.from_text(text=question),
            types.Part.from_bytes(data=image_data, mime_type="image/png")
        ]
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                temperature=1,
                top_p=0.25,
                top_k=40,
                max_output_tokens=8192,
                tools=tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            ),
            contents=content
        )
        tool_calls = response.function_calls
        response_text = response.text
        token_stats.update_token_stats(tools[0].__name__, response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count)

    elif isinstance(client, Anthropic):
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=0.7,
            system="You are a helpful assistant. Use tools when necessary.",
            tools=tools,
            messages=[user_message],
        )
        tool_calls = response.tool_calls
        response_text = response.content[0].text if response.content else ""
        # --- Added token stats for Anthropic ---
        usage = getattr(response, "usage", None)
        if usage:
            token_stats.update_token_stats(model, getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0))

    else:
        raise ValueError("Unsupported LLM Model")

    end = time.time()
    logger.debug(f"Received response from LLM {response}")
    logger.debug(f"Time taken to call LLM ***** {model} ***** : {end - start:.2f}s")

    functions_to_call = []
    if tool_calls:
        logger.debug(f"Got tool calls. Number of tool calls: {len(tool_calls)}")
        for tool in tool_calls:
            if isinstance(client, genai.Client):
                fn_name = tool.name
                fn_args = tool.args
            elif isinstance(client, Anthropic):
                fn_name = tool.name
                fn_args = tool.input
            else:
                fn_name = tool.function.name
                fn_args = tool.function.arguments
                if isinstance(client, OpenAI):
                    # Open AI returns arguments as a string with a json in it                 
                    fn_args = json.loads(fn_args)

            functions_to_call.append({
                "name": fn_name,
                "arguments": fn_args,
            })
    else:
        logger.debug("No tool calls found, attempting to parse JSON from response.")
        json_tools = _parse_llm_response_to_json(response_text)
        if json_tools:
            for key, value in json_tools.items():
                functions_to_call.append({
                    "name": key,
                    "arguments": value,
                })
    return response, functions_to_call

def _parse_llm_response_to_json(response_text):
    json_obj = None
    try:
        json_obj = json.loads(response_text)
    except json.JSONDecodeError:
        try:
            results = jsonfinder(response_text)
            for _, _, json_obj in results:
                if json_obj is not None:
                    break
        except Exception:
            pass
    if not json_obj:
        logger.error(f"Failed to parse JSON from response: {response_text}")
    return json_obj

async def process_prompt_return_json(system_prompt="", user_prompt="", chat_history=[], model="gemini-2.0-flash", purpose="navigation", site_id=0):
    prompt_to_log = system_prompt + json.dumps(chat_history, indent=2) + user_prompt
    await logger.log_text_to_file(site_id, prompt_to_log, purpose, "prompt")

    start = time.time()
    is_open_ai = model.startswith("gpt-") or model == "o3-mini"
    is_gemini_ai = model.startswith("gemini-")
    is_anthropic = model.startswith("claude-")
    is_ollama = model.startswith("deepseek") or model.startswith("qwen") or model.startswith("llama") or model.startswith("gemma")

    messages = []
    if system_prompt and not is_anthropic and not is_gemini_ai:
        messages.append({"role": "system", "content": system_prompt})
    messages += chat_history
    messages.append({"role": "user", "content": user_prompt})

    if is_open_ai:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(messages=messages, model=model)
        responsetxt = response.choices[0].message.content.strip()
        # --- Added token stats for OpenAI ---
        usage = getattr(response, "usage", None)
        if usage:
            token_stats.update_token_stats(purpose, getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0))

    elif is_gemini_ai:
        client = genai.Client(api_key=gemini_api_key)
        userContent = types.UserContent(parts=[types.Part.from_text(text=user_prompt)])
        config_args = {
            "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
            "system_instruction": system_prompt,
        }
        if model.startswith("gemini-2.5"):
            config_args["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        contents = get_history_content_for_gemini(chat_history) + [userContent]
        response = client.models.generate_content(model=model, config=types.GenerateContentConfig(**config_args), contents=contents)
        responsetxt = response.text.strip()
        token_stats.update_token_stats(purpose, response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count)

    elif is_anthropic:
        client = Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=0.7,
            system=system_prompt,
            messages=chat_history + [{"role": "user", "content": user_prompt}],
        )
        responsetxt = response.content[0].text.strip() if response.content else ""
        # --- Added token stats for Anthropic ---
        usage = getattr(response, "usage", None)
        if usage:
            token_stats.update_token_stats(purpose, getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0))

    elif is_ollama:
        client = ollama.Client()
        response = client.chat(model=model, messages=messages)
        responsetxt = response["message"].get("content")

    else:
        raise ValueError("Invalid model")

    end = time.time()
    logger.info(f"Time taken to call LLM : {end - start:.2f}s")

    responsejson = _parse_llm_response_to_json(responsetxt)
    await logger.log_text_to_file(site_id, json.dumps(responsejson, indent=2), purpose, "response")
    return responsejson

def get_history_content_for_gemini(chat_history):
    content = []
    for message in chat_history:
        if message["role"] == "user":
            content.append(types.UserContent(parts=[types.Part.from_text(text=message["content"])]))
        elif message["role"] in ["model", "assistant"]:
            content.append(types.ModelContent(parts=[types.Part.from_text(text=message["content"])]))
    return content
