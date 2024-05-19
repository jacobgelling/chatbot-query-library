#!/usr/bin/env python
"""Provides common classes for accessing numerous chatbots."""

import openai
import requests
from .cookies import CookieManager
from gemini import Gemini as GeminiAPI
import EdgeGPT.EdgeGPT as EdgeGPT
import asyncio

class _Chatbot:
    def __init__(self):
        pass

class _UnofficialChatbot(_Chatbot):
    def __init__(self):
        super().__init__()
        self.cookie_manager: CookieManager

    def rotate_cookie_file(self) -> None:
        """Rotate the cookie file."""
        self.cookie_manager.rotate_cookie_file()

    def kill_cookie_file(self) -> None:
        """Kill the cookie file."""
        self.cookie_manager.kill_cookie_file()

class OpenAI(_Chatbot):
    def __init__(self, api_key: str, name: str = "GPT-3.5", model: str = "gpt-3.5-turbo", timeout: int = 60, temperature: float = 1.0, max_tokens: int = 2048):
        """Initialise OpenAI, with defaults set to GPT-3.5."""
        super().__init__()
        openai.api_key = api_key
        self.name = name
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def query(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        if self.model in ["davinci", "curie", "babbage", "ada", "text-ada-001", "text-babbage-001", "text-curie-001"]:
            openai_response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                request_timeout=self.timeout
            )
            return openai_response.choices[0].text
        else:
            chat_completion = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                request_timeout=self.timeout
            )
            return chat_completion.choices[0].message.content

class Copilot(_UnofficialChatbot):
    def __init__(self, cookie_manager: CookieManager = CookieManager(domain_name="bing.com"), name: str = "Copilot", timeout: int = 60, temperature: EdgeGPT.ConversationStyle = EdgeGPT.ConversationStyle.balanced):
        """Initialise Copilot."""
        super().__init__()
        self.cookie_manager = cookie_manager
        self.name = name
        self.timeout = timeout
        self.temperature = temperature

    def temperature_to_string(self) -> str :
        """Convert the temperature attribute to a string."""
        if self.temperature == EdgeGPT.ConversationStyle.balanced:
            return "Balanced"
        elif self.temperature == EdgeGPT.ConversationStyle.precise:
            return "Precise"
        elif self.temperature == EdgeGPT.ConversationStyle.creative:
            return "Creative"

    def query(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        # Rotate the cookie file and get the cookies
        self.rotate_cookie_file()
        cookie_list = self.cookie_manager.get_cookie_list()
        
        # Return the response
        async def query_with_timeout(prompt: str, timeout: int):
            bot = await EdgeGPT.Chatbot.create(cookies=cookie_list)
            response = await asyncio.wait_for(
                bot.ask(prompt=prompt, conversation_style=self.temperature, simplify_response=True),
                timeout=timeout
            )
            return response["text"]
        answer = asyncio.run(query_with_timeout(prompt, self.timeout))
        return answer

class Gemini(_UnofficialChatbot):
    def __init__(self, cookie_manager: CookieManager = CookieManager(domain_name="google.com"), name: str = "Gemini", timeout: int = 60):
        """Initialise Gemini."""
        super().__init__()
        self.cookie_manager = cookie_manager
        self.name = name
        self.timeout = timeout
        self.temperature = None

    def query(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        # Rotate the cookie file and get the cookies
        self.rotate_cookie_file()
        cookie_dict = self.cookie_manager.get_cookie_dict()

        # Return the response
        gemini = GeminiAPI(cookies=cookie_dict, timeout=self.timeout)
        answer = gemini.generate_content(prompt).text
        return answer

class HuggingFace(_Chatbot):
    def __init__(self, api_key: str, name: str = "Llama 2", model: str = "meta-llama/Llama-2-70b-chat-hf", timeout: int = 60, temperature: float = 0.6, max_tokens: int = 2048, top_p: float = 0.9, top_k: int = 0):
        """Initialise Hugging Face, with defaults set to Llama 2."""
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k

    def query(self, prompt: str) -> str:
        """Generate a response based on the provided prompt."""
        api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.model == "meta-llama/Llama-2-70b-chat-hf":
            system_prompt = "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
            complete_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
        else:
            complete_prompt = prompt
        data = {
            "inputs": complete_prompt,
            "parameters": {
                "top_k": self.top_k,
                "top_p": self.top_p,
                "temperature": self.temperature,
                "max_new_tokens": self.max_tokens,
                "max_time": self.timeout,
                "return_full_text": False,
            },
            "options": {
                "use_cache": False,
                "wait_for_model": True,
            },
        }
        response = requests.request("POST", api_url, headers=headers, json=data, timeout=self.timeout).json()
        
        # Check response for errors
        if len(response) == 0:
            raise Exception("No response.")
        elif "error" in response:
            raise Exception(response["error"])
        else:
            return response[0]["generated_text"]
