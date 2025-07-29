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

class PromptTemplateProcessor:
    def __init__(self, template_path: str):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template file not found: '{template_path}'. Please check the path and try again.")

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
