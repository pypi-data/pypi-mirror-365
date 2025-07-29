
# import requests
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class OllamaLLMWrapper(LLMBase):
#     def __init__(self, model_name: str, host: str):
#         self.model_name = model_name
#         self.host = host
#         self.api_url = f"{self.host}/api/generate"
#         print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")
#
#     def get_data(self, prompt: str) -> str:
#         try:
#             print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             payload = {
#                 "model": self.model_name,
#                 "prompt": formatted_prompt,
#                 "stream": False
#             }
#
#             response = requests.post(self.api_url, json=payload)
#             response.raise_for_status()
#             return "[Ollama] " + response.json().get("response", "[No response]")
#         except Exception as e:
#             return f"[Ollama ERROR]: {str(e)}"


from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class OllamaLLMWrapper(LLMBase):
    def __init__(self, model_name: str, host: str):
        self.model_name = model_name
        self.host = host  # Used for base_url
        #  Initialize LangChain OllamaLLM
        self.llm = OllamaLLM(model=self.model_name, base_url=self.host)
        print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")

    def get_data(self, prompt: str) -> str:
        try:
            print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)

            #  Use LangChain OllamaLLM invoke method
            response = self.llm.invoke(formatted_prompt)
            print(response)
            result = response.text.strip()
            return "[Ollama] " + response
        except Exception as e:
            return f"[Ollama ERROR]: {str(e)}"



# from langchain_ollama import OllamaLLM
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class OllamaLLMWrapper(LLMBase):
#     def __init__(self, model_name: str, host: str):
#         self.model_name = model_name
#         self.host = host
#         self.llm = OllamaLLM(model=self.model_name, base_url=self.host)
#         print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")
#
#     def get_data(self, prompt: str) -> dict:
#         try:
#             print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             response = self.llm.invoke(formatted_prompt)
#
#             # LangChain Ollama doesn't expose token usage directly (as of now), so return N/A
#             return {
#                 "response": "[Ollama] " + response,
#                 "prompt_tokens": "N/A",
#                 "completion_tokens": "N/A",
#                 "total_tokens": "N/A"
#             }
#
#         except Exception as e:
#             return {
#                 "response": f"[Ollama ERROR]: {str(e)}",
#                 "prompt_tokens": None,
#                 "completion_tokens": None,
#                 "total_tokens": None
#             }
