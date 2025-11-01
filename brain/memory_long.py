from pathlib import Path
import json, time
from rapidfuzz import fuzz

class LongMemory:
    """
    Mémoire long terme persistante (JSON) + recherche par similarité (RapidFuzz).
    Non bloquante, légère, locale.
    """
    def __init__(self, path="/home/pi/tshakongo/long_memory.json", size=2000, th=80):
        self.path = Path(path); self.size = size; self.th = th
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"facts": []})

    def _read(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"facts": []}

    def _write(self, obj):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def add(self, text:str, tags=None):
        data = self._read()
        tags = tags or []
        data["facts"].append({"t": time.time(), "text": text, "tags": tags})
        if len(data["facts"]) > self.size:
            data["facts"] = data["facts"][-self.size:]
        self._write(data)
        return True

    def search(self, query:str, top_k=5):
        data = self._read()["facts"]
        scored = []
        for f in data:
            s = fuzz.QRatio(query, f["text"])
            if s >= self.th:
                scored.append((s, f))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [f for s,f in scored[:top_k]]

    def dump(self): return self._read()["facts"]
