
import json, os, time
from pathlib import Path
class Memory:
    def __init__(self, path="/home/pi/tshakongo/memory.json", max_items=500):
        self.path = Path(path); self.max_items = max_items
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({"facts":{}, "log":[]})
    def _read(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception: return {"facts":{}, "log":[]}
    def _write(self, obj):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8"); tmp.replace(self.path)
    def set_fact(self, key, value):
        data = self._read(); data["facts"][key] = value; self._write(data); return f"Fait mémorisé: {key} = {value}"
    def get_fact(self, key):
        data = self._read(); return data["facts"].get(key)
    def all_facts(self): return self._read()["facts"]
    def log_turn(self, user_text, assistant_text):
        data = self._read(); data["log"].append({"t": time.time(), "u": user_text, "a": assistant_text})
        if len(data["log"]) > self.max_items: data["log"] = data["log"][-self.max_items:]
        self._write(data)
    def history(self, n=50):
        data = self._read(); return data["log"][-n:]
