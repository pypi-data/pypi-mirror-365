# Template config file for all supported LLM providers
# Fill in only the providers you want to use

config = {
    # Set the provider you want to use
    "provider": "openai",  # e.g. "openai", "azure", "bedrock", "anthropic", "ai21", "mistral", "meta", "groq", "cohere", "google", "local", "replicate", "ibm", "mosaicml", "perplexity", "bard", "huggingface"

    # OpenAI (ChatGPT, GPT-4, GPT-3.5, etc.)
    "openai": {
        "api_key": "sk-...",
        "model": "gpt-4",
        "base_url": None,
        "organization": None,
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Azure OpenAI Service
    "azure": {
        "api_key": "...",
        "endpoint": "https://...",
        "deployment": "...",
        "model": None,
        "api_version": None,
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Anthropic (Claude, direct API)
    "anthropic": {
        "api_key": "...",
        "model": "claude-3-opus-20240229",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Amazon Bedrock (Anthropic, AI21, Cohere, Meta, etc.)
    "bedrock": {
        "aws_access_key": "...",
        "aws_secret_key": "...",
        "region": "us-east-1",
        "model": "anthropic.claude-v2",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Cohere
    "cohere": {
        "api_key": "...",
        "model": "command",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # AI21 Labs (Jurassic)
    "ai21": {
        "api_key": "...",
        "model": "j2-ultra",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Mistral AI
    "mistral": {
        "api_key": "...",
        "model": "mistral-large",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Meta (Llama, via local or cloud)
    "meta": {
        "endpoint_url": "http://localhost:8000",
        "model": "llama-3",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Groq
    "groq": {
        "api_key": "...",
        "model": "llama-3-70b",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Google Vertex AI (Gemini, PaLM, etc.)
    "google": {
        "api_key": "...",
        "project": "...",
        "location": "us-central1",
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Local LLMs (Ollama, LM Studio, vLLM, etc.)
    "local": {
        "endpoint_url": "http://localhost:8000",
        "model": "llama-3",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Replicate (API for many open models)
    "replicate": {
        "api_key": "...",
        "model": "meta/llama-3-70b-instruct",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # IBM watsonx.ai
    "ibm": {
        "api_key": "...",
        "project_id": "...",
        "model": "...",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Databricks MosaicML
    "mosaicml": {
        "api_key": "...",
        "model": "mpt-30b",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Perplexity AI
    "perplexity": {
        "api_key": "...",
        "model": "pplx-70b-chat",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Google Bard (API, if available)
    "bard": {
        "api_key": "...",
        "model": "bard",
        "temperature": 0.7,
        "max_tokens": 1024
    },
    # Hugging Face Inference API
    "huggingface": {
        "api_key": "...",
        "model": "meta-llama/Llama-2-70b-chat-hf",
        "temperature": 0.7,
        "max_tokens": 1024
    }
}
