import os
import tempfile
import pytest
from prompter.llm_factory import get_llm_service

# Dummy provider for test
class DummyService:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
    def generate(self, prompt: str, **kwargs) -> str:
        return f"{self.api_key}:{self.model}:{prompt}"

def test_openai_dynamic_import(monkeypatch):
    # Patch importlib to return DummyService
    import importlib
    monkeypatch.setattr(importlib, "import_module", lambda name: type('M', (), {"OpenAIService": DummyService}))
    # Create a temp YAML config
    config = '''
provider: openai
openai:
  api_key: testkey
  model: testmodel
'''
    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as f:
        f.write(config)
        f.flush()
        svc = get_llm_service(f.name)
        assert isinstance(svc, DummyService)
        assert svc.api_key == "testkey"
        assert svc.model == "testmodel"
        assert svc.generate("hello") == "testkey:testmodel:hello"
    os.unlink(f.name)

def test_env_priority(monkeypatch):
    # Patch importlib to return DummyService
    import importlib
    monkeypatch.setattr(importlib, "import_module", lambda name: type('M', (), {"OpenAIService": DummyService}))
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_OPENAI_API_KEY", "envkey")
    monkeypatch.setenv("LLM_OPENAI_MODEL", "envmodel")
    svc = get_llm_service(None)
    assert isinstance(svc, DummyService)
    assert svc.api_key == "envkey"
    assert svc.model == "envmodel"
    assert svc.generate("hi") == "envkey:envmodel:hi"
