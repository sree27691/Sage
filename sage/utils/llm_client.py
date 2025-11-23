import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

load_dotenv()

class LLMClient:
    def __init__(self):
        self.models_config = self._load_models_config()
        
        # Initialize OpenAI Client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
        # Initialize Anthropic Client
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = None
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)

        # Initialize Gemini Client
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)

    def _load_models_config(self) -> Dict[str, str]:
        config_path = os.path.join(os.path.dirname(__file__), "../../config/models_config.json")
        with open(config_path, "r") as f:
            return json.load(f)

    def get_model_name(self, agent_name: str) -> str:
        llm_models = self.models_config.get("llm_models", {})
        return llm_models.get(agent_name, "gpt-4o")

    def generate_response(self, system_prompt: str, user_content: str, agent_name: str, response_format: Optional[Any] = None, temperature: float = 0.0) -> str:
        model = self.get_model_name(agent_name)
        
        if "gpt" in model.lower():
            return self._call_openai(model, system_prompt, user_content, response_format, temperature)
        elif "claude" in model.lower():
            return self._call_anthropic(model, system_prompt, user_content, temperature)
        elif "gemini" in model.lower():
            return self._call_gemini(model, system_prompt, user_content, response_format, temperature)
        else:
            # Fallback or other providers
            raise ValueError(f"Unsupported model provider for model: {model}")

    def _call_openai(self, model: str, system_prompt: str, user_content: str, response_format: Optional[Any] = None, temperature: float = 0.0) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI API key not found.")
            
        # If JSON mode is requested, ensure the prompt mentions JSON
        if response_format:
            user_content = f"{user_content}\n\nPlease respond with valid JSON."
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if response_format:
            kwargs["response_format"] = {"type": "json_object"}
            
        try:
            response = self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise e

    def _call_anthropic(self, model: str, system_prompt: str, user_content: str, temperature: float = 0.0) -> str:
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not found.")
            
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_content}
                ],
                max_tokens=4096,
                temperature=temperature
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Anthropic: {e}")
            raise e

    def _call_gemini(self, model: str, system_prompt: str, user_content: str, response_format: Optional[Any] = None, temperature: float = 0.0) -> str:
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not found.")
            
        try:
            # Gemini implementation details might vary by version, using generic approach
            gemini_model = genai.GenerativeModel(model)
            
            # Construct prompt with system instruction (if supported by model/lib version) or prepend it
            full_prompt = f"System Instruction: {system_prompt}\n\nUser Request: {user_content}"
            
            generation_config = {"temperature": temperature}
            if response_format:
                generation_config["response_mime_type"] = "application/json"

            response = gemini_model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            raise e
