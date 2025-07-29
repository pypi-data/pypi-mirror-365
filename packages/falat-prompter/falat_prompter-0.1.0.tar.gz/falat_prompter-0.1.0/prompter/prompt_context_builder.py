class PromptContextBuilder:
    def __init__(self):
        self._context = {}

    def set(self, key, value):
        if key in self._context:
            raise ValueError(f"Duplicate key '{key}' in context.")
        self._context[key] = value
        return self

    def build(self):
        return self._context

    def _format_bullets(self, items):
        return '\n'.join(f"- {item}" for item in items)

    def text(self, text):
        return self.set('text', text)
    def summary_length(self, text):
        return self.set('summary_length', text)
    def context(self, text):
        return self.set('context', text)
    def instruction(self, text):
        return self.set('instruction', text)
    def examples(self, text):
        if isinstance(text, list):
            return self.set('examples', self._format_bullets(text))
        return self.set('examples', text)
    def role(self, text):
        return self.set('role', text)
    def retrieved_docs(self, text):
        if isinstance(text, list):
            return self.set('retrieved_docs', self._format_bullets(text))
        return self.set('retrieved_docs', text)
    def question(self, text):
        return self.set('question', text)
    def answer(self, text):
        return self.set('answer', text)
    def persona(self, text):
        if isinstance(text, list):
            return self.set('persona', self._format_bullets(text))
        return self.set('persona', text)
    def history(self, text):
        if isinstance(text, list):
            return self.set('history', self._format_bullets(text))
        return self.set('history', text)
    def user_input(self, text):
        return self.set('user_input', text)
    def input_data(self, text):
        if isinstance(text, list):
            return self.set('input_data', self._format_bullets(text))
        return self.set('input_data', text)
    def transformation(self, text):
        return self.set('transformation', text)
    def output(self, text):
        if isinstance(text, list):
            return self.set('output', self._format_bullets(text))
        return self.set('output', text)
