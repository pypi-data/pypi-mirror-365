import logging

from ..context import current_activity


class AddIndentExtra(logging.Filter):
    def __init__(self, char: str = "."):
        super().__init__("indent")
        self.char = char

    def filter(self, record: logging.LogRecord) -> bool:
        node = current_activity.get()
        indent = self.char * (node.depth or 1) if node else self.char
        setattr(record, self.name, indent)
        return True
