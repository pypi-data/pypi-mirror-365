def test_local_service_importerror(monkeypatch):
    # Simulate requests not installed by patching importlib.import_module
    import importlib
    orig_import_module = importlib.import_module
    def fake_import_module(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("The 'requests' package is required for this provider. Install with: pip install requests")
        return orig_import_module(name, *args, **kwargs)
    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    from prompter.providers.local_service import LocalLLMService
    svc = LocalLLMService(endpoint_url="http://localhost:8000/generate", model="llama-test")
    with pytest.raises(ImportError) as excinfo:
        svc.generate("hello world")
    assert "requests" in str(excinfo.value)
    assert "pip install requests" in str(excinfo.value)
import pytest
from prompter.providers.local_service import LocalLLMService

def test_local_service_no_api_call(monkeypatch):
    try:
        import requests
    except ImportError:
        pytest.skip("requests not installed")
    # Patch requests.post to avoid real HTTP call
    class DummyResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {"text": "dummy output"}
    monkeypatch.setattr(requests, "post", lambda url, json: DummyResponse())

    svc = LocalLLMService(endpoint_url="http://localhost:8000/generate", model="llama-test")
    result = svc.generate("hello world")
    assert result == "dummy output"
