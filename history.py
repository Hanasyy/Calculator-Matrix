import time
from file_utils import save_history, load_history

class History:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self._list = load_history(self.filename)

    def add(self, entry):
        # entry: dict with keys "time", "operation", "result"
        entry = dict(entry)
        entry.setdefault("time", time.strftime("%Y-%m-%d %H:%M:%S"))
        self._list.append(entry)
        save_history(self._list, self.filename)

    def all(self):
        return list(self._list)

    def clear(self):
        self._list = []
        save_history(self._list, self.filename)
