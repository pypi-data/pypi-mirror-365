import os
import tempfile
import pytest
from prompter.prompt_template_processor import PromptTemplateProcessor

def test_basic_variable():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
        tf.write('Hello, {{name}}!')
        tf.flush()
        processor = PromptTemplateProcessor(tf.name)
        result = processor.render({'name': 'World'})
        assert result == 'Hello, World!'
    os.unlink(tf.name)

def test_function_no_params():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
        tf.write('Greeting: {{greet}}')
        tf.flush()
        processor = PromptTemplateProcessor(tf.name)
        result = processor.render({'greet': lambda: 'Hi there'})
        assert result == 'Greeting: Hi there'
    os.unlink(tf.name)

def test_function_with_params():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
        tf.write('Sum: {{add}}')
        tf.flush()
        processor = PromptTemplateProcessor(tf.name)
        def add(a, b):
            return str(a + b)
        result = processor.render({'add': add, 'a': 2, 'b': 3})
        assert result == 'Sum: 5'
    os.unlink(tf.name)

def test_missing_param():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
        tf.write('Sum: {{add}}')
        tf.flush()
        processor = PromptTemplateProcessor(tf.name)
        def add(a, b):
            return str(a + b)
        with pytest.raises(ValueError) as excinfo:
            processor.render({'add': add, 'a': 2})
        assert 'Missing required parameters' in str(excinfo.value)
    os.unlink(tf.name)

def test_template_file_not_found():
    with pytest.raises(FileNotFoundError) as excinfo:
        PromptTemplateProcessor('non_existent_template_file.txt')
    assert "Prompt template file not found" in str(excinfo.value)
