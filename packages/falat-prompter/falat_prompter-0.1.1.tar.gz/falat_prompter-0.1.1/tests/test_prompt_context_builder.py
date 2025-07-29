import pytest
from prompter.prompt_context_builder import PromptContextBuilder

def test_text_and_instruction():
    builder = PromptContextBuilder()
    ctx = builder.text('hello').instruction('summarize').build()
    assert ctx['text'] == 'hello'
    assert ctx['instruction'] == 'summarize'

def test_examples_bulleted():
    builder = PromptContextBuilder()
    ctx = builder.examples(['a', 'b', 'c']).build()
    assert ctx['examples'] == '- a\n- b\n- c'

def test_examples_string():
    builder = PromptContextBuilder()
    ctx = builder.examples('single example').build()
    assert ctx['examples'] == 'single example'

def test_retrieved_docs_bulleted():
    builder = PromptContextBuilder()
    ctx = builder.retrieved_docs(['doc1', 'doc2']).build()
    assert ctx['retrieved_docs'] == '- doc1\n- doc2'

def test_persona_and_history_bulleted():
    builder = PromptContextBuilder()
    ctx = builder.persona(['p1', 'p2']).history(['h1', 'h2']).build()
    assert ctx['persona'] == '- p1\n- p2'
    assert ctx['history'] == '- h1\n- h2'

def test_input_data_and_output_bulleted():
    builder = PromptContextBuilder()
    ctx = builder.input_data(['i1', 'i2']).output(['o1', 'o2']).build()
    assert ctx['input_data'] == '- i1\n- i2'
    assert ctx['output'] == '- o1\n- o2'

def test_duplicate_key_raises():
    builder = PromptContextBuilder()
    builder.text('a')
    with pytest.raises(ValueError):
        builder.text('b')
