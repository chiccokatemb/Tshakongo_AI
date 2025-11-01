
from pathlib import Path

class FSSandbox:
    def __init__(self, allowlist, log_fn=print):
        self.roots = [Path(p).resolve() for p in allowlist]
        self.log = log_fn

    def _ok(self, p: Path) -> bool:
        rp = Path(p).resolve()
        return any(str(rp).startswith(str(root)) for root in self.roots)

    def mkdir(self, path:str)->str:
        p = Path(path)
        if not self._ok(p): return "Chemin non autorisé."
        p.mkdir(parents=True, exist_ok=True)
        self.log(f"[FS] mkdir {p}")
        return f"Dossier créé: {p}"

    def listdir(self, path:str)->str:
        p = Path(path)
        if not self._ok(p): return "Chemin non autorisé."
        if not p.exists(): return "Chemin introuvable."
        return "\n".join(sorted(x.name for x in p.iterdir()))
