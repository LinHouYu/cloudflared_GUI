import json
import os

class Storage:
    def __init__(self, filename="data/user.json"):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({"settings": {"theme": "light"}, "last": {}}, f, ensure_ascii=False, indent=2)

    def _load(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_settings(self):
        return self._load().get("settings", {})

    def save_settings(self, settings: dict):
        data = self._load()
        data["settings"] = settings
        self._save(data)

    def save_last(self, tab: str, tunnel: str, port: str):
        data = self._load()
        data.setdefault("last", {})
        data["last"][tab] = {"tunnel": tunnel, "port": port}
        self._save(data)

    def load_last(self, tab: str):
        return self._load().get("last", {}).get(tab, {})
