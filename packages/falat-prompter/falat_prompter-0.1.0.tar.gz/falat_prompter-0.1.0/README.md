# Prompter: Extensible LLM Provider System

Prompter is a flexible, plugin-style Python framework for working with multiple Large Language Model (LLM) providers. It supports dynamic provider loading, robust error handling, and unified response parsing, making it easy to integrate, extend, and use in any open source or production environment.

## Features
- **Plugin-style LLM providers**: Easily add or swap providers (OpenAI, Cohere, Anthropic, etc.)
- **Optional SDKs**: Only install what you need; clear errors if a provider's SDK is missing
- **Unified response handling**: Consistent, type-safe output from all providers
- **Prompting flexibility**: Use prompt templates or build prompts programmatically
- **Extensible and testable**: Add new providers or prompt strategies with minimal code

## Concepts

### 1. Prompt Creation
- **Template File Way**: Define prompts in external template files (e.g., Jinja2, plain text) and load them at runtime. This enables easy prompt management and reuse.
- **Programmatic Way**: Build prompts dynamically in code using string formatting, f-strings, or other logic. This is useful for advanced or highly dynamic use cases.

### 2. Service Providers
- Each provider (OpenAI, Cohere, Anthropic, etc.) is a class with a unified `generate` method.
- Providers are loaded dynamically and only require their SDK if used.
- All providers support structured output via a `result_object` parameter, enabling type-safe parsing of LLM responses.

## Usage Example
```python
from prompter.providers import OpenAIService

service = OpenAIService(api_key="sk-...", model="gpt-4")
response = service.generate("What is the capital of France?")
print(response)  # "Paris"
```

## Extending
- Add new providers by subclassing and implementing the `generate` method.
- Add new prompt strategies by creating new template loaders or programmatic builders.

## License
MIT

## Contributing
Pull requests and issues are welcome! Please see CONTRIBUTING.md for guidelines.
