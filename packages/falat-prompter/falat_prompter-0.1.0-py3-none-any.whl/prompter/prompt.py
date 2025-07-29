import os
from typing import Callable, Dict, Any

class Prompt:
    def __init__(self, template: str):
        self.template = template
        self.sections = self._parse_sections(template)
        self.values = {}

    @classmethod
    def load_template(cls, rel_path: str, base_dir: str = None):
        """
        Load a prompt from a template file by relative path (without extension).
        Example: load_template('summarization/summarization')
        """
        base_dir = base_dir or os.path.join(os.path.dirname(__file__), '..', 'templates')
        path = os.path.join(base_dir, rel_path + '.prompt')
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()
        return cls(template)

    @classmethod
    def from_type(cls, type_: str, base_dir: str = None):
        """
        Create a prompt object by template type, using the default template for that type.
        """
        base_dir = base_dir or os.path.join(os.path.dirname(__file__), '..', 'templates')
        # Use the first .prompt file found in the type folder
        type_dir = os.path.join(base_dir, type_)
        for fname in os.listdir(type_dir):
            if fname.endswith('.prompt'):
                with open(os.path.join(type_dir, fname), 'r', encoding='utf-8') as f:
                    template = f.read()
                return cls(template)
        raise FileNotFoundError(f"No .prompt file found for type '{type_}' in '{type_dir}'")

    def _parse_sections(self, template: str) -> Dict[str, str]:
        # Simple parser: sections are lines starting with a keyword and ':'
        sections = {}
        current = None
        lines = template.splitlines()
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip().lower()
                sections[key] = val.strip()
                current = key
            elif current:
                sections[current] += '\n' + line
        return sections

    def set(self, section: str, value: Any):
        self.values[section.lower()] = value
        return self

    # Section methods: accept value or callable
    def context(self, value):
        return self.set('context', value)
    def instruction(self, value):
        return self.set('instruction', value)
    def examples(self, value):
        return self.set('examples', value)
    def role(self, value):
        return self.set('role', value)
    def retrieved_docs(self, value):
        return self.set('retrieved_docs', value)
    def question(self, value):
        return self.set('question', value)
    def answer(self, value):
        return self.set('answer', value)
    def text(self, value):
        return self.set('text', value)
    def summary_length(self, value):
        return self.set('summary_length', value)
    def persona(self, value):
        return self.set('persona', value)
    def history(self, value):
        return self.set('history', value)
    def user_input(self, value):
        return self.set('user_input', value)
    def input_data(self, value):
        return self.set('input_data', value)
    def transformation(self, value):
        return self.set('transformation', value)
    def output(self, value):
        return self.set('output', value)


    def context(self, value: str):
        return self.set('context', value)

    def instruction(self, value: str):
        return self.set('instruction', value)

    def examples(self, value: str):
        return self.set('examples', value)

    def role(self, value: str):
        return self.set('role', value)

    def retrieved_docs(self, value: str):
        return self.set('retrieved_docs', value)

    def question(self, value: str):
        return self.set('question', value)

    def answer(self, value: str):
        return self.set('answer', value)

    def text(self, value: str):
        return self.set('text', value)

    def summary_length(self, value: int):
        return self.set('summary_length', value)

    def persona(self, value: str):
        return self.set('persona', value)

    def history(self, value: str):
        return self.set('history', value)

    def user_input(self, value: str):
        return self.set('user_input', value)

    def input_data(self, value: str):
        return self.set('input_data', value)

    def transformation(self, value: str):
        return self.set('transformation', value)

    def output(self, value: str):
        return self.set('output', value)

    def render(self):
        import inspect
        result = self.template
        for k, v in self.values.items():
            value = v
            if callable(v):
                sig = inspect.signature(v)
                # Pass context values as kwargs if function expects them
                kwargs = {kk: vv for kk, vv in self.values.items() if kk in sig.parameters}
                value = v(**kwargs) if kwargs else v()
            result = result.replace(f"{{{{{k}}}}}", str(value))
        return result

# Example usage:
# prompt = Prompt.load_template('summarization', 'summarization')
# prompt.summarize(text="Long text...", summary_length=2)
# print(prompt.render())
