
import os
import importlib
from prompter.llm_config_loader import load_llm_config

class LLMService:
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

class OpenAIService(LLMService):
    def __init__(self, api_key, model="gpt-4"):
        self.api_key = api_key
        self.model = model
    def generate(self, prompt: str, **kwargs) -> str:
        # Implement OpenAI API call here
        pass

class BedrockService(LLMService):
    def __init__(self, aws_access_key, aws_secret_key, region, model):
        pass
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class LocalLLMService(LLMService):
    def __init__(self, endpoint_url, model=None):
        self.endpoint_url = endpoint_url
        self.model = model
    def generate(self, prompt: str, **kwargs) -> str:
        pass


def get_llm_service(config_path: str = None) -> LLMService:
    """
    Dynamically load the LLM service provider class from the providers directory based on config.
    """
    config = load_llm_config(config_path)
    provider = config.get("provider")
    if not provider:
        raise ValueError("No provider specified in config.")
    provider_config = config.get(provider, {})
    module_name = f"prompter.providers.{provider}_service"
    # Guess class name: handle special cases for capitalization (e.g., OpenAI, Cohere, AI21, etc.)
    SPECIAL_CLASS_NAMES = {
        "openai": "OpenAIService",
        "cohere": "CohereService",
        "ai21": "AI21Service",
        "anthropic": "AnthropicService",
        "mistral": "MistralService",
        "meta": "MetaLlamaService",
        "google": "GoogleVertexAIService",
        "ibm": "IBMWatsonService",
        "huggingface": "HuggingFaceService",
        "local": "LocalLLMService",
        "groq": "GroqService",
        "replicate": "ReplicateService",
        "mosaicml": "MosaicMLService",
        "perplexity": "PerplexityService",
        "bard": "BardService",
    }
    def to_camel(s):
        return ''.join(word.capitalize() for word in s.split('_'))
    class_name = SPECIAL_CLASS_NAMES.get(provider, to_camel(provider) + "Service")

    try:
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import provider class {class_name} from {module_name}: {e}")

    return provider_class(**provider_config)
