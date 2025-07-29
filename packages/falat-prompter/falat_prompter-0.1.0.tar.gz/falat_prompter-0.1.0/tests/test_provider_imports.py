import pytest
import importlib

PROVIDERS = [
    ("openai", "prompter.providers.openai_service", "OpenAIService", "openai"),
    ("cohere", "prompter.providers.cohere_service", "CohereService", "cohere"),
    ("anthropic", "prompter.providers.anthropic_service", "AnthropicService", "anthropic"),
    ("azure", "prompter.providers.azure_service", "AzureOpenAIService", "openai"),
    ("google", "prompter.providers.google_service", "GoogleVertexAIService", "google.cloud.aiplatform"),
    ("huggingface", "prompter.providers.huggingface_service", "HuggingFaceService", "requests"),
    ("ai21", "prompter.providers.ai21_service", "AI21Service", "requests"),
    ("bedrock", "prompter.providers.bedrock_service", "BedrockService", "boto3"),
    ("meta", "prompter.providers.meta_service", "MetaLlamaService", "requests"),
    ("mistral", "prompter.providers.mistral_service", "MistralService", "requests"),
    ("replicate", "prompter.providers.replicate_service", "ReplicateService", "requests"),
    ("perplexity", "prompter.providers.perplexity_service", "PerplexityService", "requests"),
    ("bard", "prompter.providers.bard_service", "BardService", "requests"),
    ("groq", "prompter.providers.groq_service", "GroqService", "requests"),
    ("mosaicml", "prompter.providers.mosaicml_service", "MosaicMLService", "requests"),
    ("ibm", "prompter.providers.ibm_service", "IBMWatsonService", "requests"),
]

def make_importerror_test(module_path, class_name, sdk_name):
    def test_func(monkeypatch):
        # Patch importlib.import_module to raise ImportError for the SDK
        orig_import_module = importlib.import_module
        def fake_import_module(name, *args, **kwargs):
            if name == sdk_name:
                raise ImportError(f"The '{sdk_name}' package is required for this provider. Install with: pip install {sdk_name}")
            return orig_import_module(name, *args, **kwargs)
        monkeypatch.setattr(importlib, "import_module", fake_import_module)
        mod = importlib.import_module(module_path)
        # Provide all required dummy args for each provider
        args = {
            "OpenAIService": ("dummy",),
            "CohereService": ("dummy",),
            "AnthropicService": ("dummy",),
            "AzureOpenAIService": ("dummy", "dummy", "dummy"),
            "GoogleVertexAIService": ("dummy", "dummy", "dummy"),
            "HuggingFaceService": ("dummy", "dummy"),
            "AI21Service": ("dummy",),
            "BedrockService": ("dummy", "dummy", "dummy", "dummy"),
            "MetaLlamaService": ("dummy",),
            "MistralService": ("dummy",),
            "ReplicateService": ("dummy", "dummy"),
            "PerplexityService": ("dummy", "dummy"),
            "BardService": ("dummy",),
            "GroqService": ("dummy",),
            "MosaicMLService": ("dummy", "dummy"),
            "IBMWatsonService": ("dummy", "dummy", "dummy"),
        }
        svc = getattr(mod, class_name)(*args[class_name])
        with pytest.raises(ImportError) as excinfo:
            svc.generate("hello world")
        assert sdk_name in str(excinfo.value)
        # For Google, expect pip package name, not import name
        pip_name = sdk_name
        if sdk_name == "google.cloud.aiplatform":
            pip_name = "google-cloud-aiplatform"
        assert f"pip install {pip_name}" in str(excinfo.value)
    return test_func

# Dynamically create a test for each provider
for provider, module_path, class_name, sdk_name in PROVIDERS:
    test_name = f"test_{provider}_importerror"
    globals()[test_name] = make_importerror_test(module_path, class_name, sdk_name)
