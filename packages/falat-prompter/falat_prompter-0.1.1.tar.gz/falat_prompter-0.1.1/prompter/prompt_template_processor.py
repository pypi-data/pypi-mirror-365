import re
import inspect
from typing import Callable, Dict, Optional, Union


def replacer(match, context):
    key = match.group(1)
    value = context.get(key)
    if callable(value):
        sig = inspect.signature(value)
        kwargs = {k: v for k, v in context.items() if k in sig.parameters}
        missing = [p for p in sig.parameters if p not in kwargs and sig.parameters[p].default is inspect.Parameter.empty]
        if missing:
            raise ValueError(f"Missing required parameters for function '{key}': {', '.join(missing)}")
        return value(**kwargs)
    return str(value) if value is not None else match.group(0)


import importlib.resources
import requests
import os

class PromptTemplateProcessor:
    def __init__(self, template_name: str, package: str = None, url: str = None):
        """
        Load a template from a file path, package resource, or URL.
        - template_name: The template file name or path.
        - package: If provided, loads from the given package using importlib.resources.
        - url: If provided, downloads the template from the given URL.
        """
        if url:
            response = requests.get(url)
            response.raise_for_status()
            self.template = response.text
        elif package:
            with importlib.resources.open_text(package, template_name) as f:
                self.template = f.read()
        else:
            if not os.path.isfile(template_name):
                raise FileNotFoundError(f"Prompt template file not found: '{template_name}'. Please check the path and try again.")
            with open(template_name, 'r', encoding='utf-8') as f:
                self.template = f.read()

    def render(self, context: Dict[str, Union[str, Callable[[], str]]]) -> str:
        rendered = re.sub(r'{{\s*(\w+)\s*}}', lambda m: replacer(m, context), self.template)
        # Optionally, parse sections like 'Context:', 'Instruction:'
        # If you want to support heading-based parsing, add logic here
        return rendered

# Usage example:
# processor = PromptTemplateProcessor('my_template.txt')
# prompt = processor.render({
#     'context': 'You are a Python expert.',
#     'instruction': 'Write a function to add two numbers.',
#     'examples': 'Input: 2, 3; Output: 5'
# })
# print(prompt)
