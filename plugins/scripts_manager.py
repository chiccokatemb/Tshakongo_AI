
from pathlib import Path
import subprocess, uuid

class ScriptsManager:
    def __init__(self, root_dir:str, docker_image:str, network:str, mem_limit:str, cpus:str, timeout_sec:int, enable_native:bool=False, log_fn=print):
        self.root = Path(root_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.image = docker_image; self.network = network; self.mem_limit = mem_limit; self.cpus = cpus; self.timeout = timeout_sec
        self.enable_native = enable_native; self.log = log_fn
    def _allowed(self, p:Path)->bool:
        try: rp = p.resolve(); return str(rp).startswith(str(self.root))
        except Exception: return False
    def create(self, name:str, content:str)->str:
        if not name.endswith(".py"): return "Le nom doit se terminer par .py"
        p = (self.root / name); 
        if not self._allowed(p): return "Chemin non autorisé"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8"); return f"Script créé: {p.name}"
    def list(self): return sorted([str(p.relative_to(self.root)) for p in self.root.rglob("*.py")])
    def read(self, name:str):
        p = (self.root / name); 
        if not self._allowed(p) or not p.exists(): return None
        return p.read_text(encoding="utf-8")
    def delete(self, name:str, confirm:bool=False)->str:
        p = (self.root / name)
        if not self._allowed(p) or not p.exists(): return "Introuvable"
        if not confirm: return "Confirme la suppression"
        p.unlink(); return f"Supprimé: {name}"
    def run_docker(self, name:str, args:list=None):
        args = args or []; p = (self.root / name)
        if not self._allowed(p) or not p.exists(): return {"ok": False, "out": "Script non trouvé"}
        cid = f"tsk-{uuid.uuid4().hex[:8]}"
        cmd = ["docker","run","--rm","--name",cid,f"--memory={self.mem_limit}",f"--cpus={self.cpus}",f"--network={self.network}","-v",f"{self.root}:/scripts:ro",self.image,"python","-u",f"/scripts/{name}",*args]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout); 
            return {"ok": proc.returncode==0, "out": (proc.stdout+proc.stderr)}
        except subprocess.TimeoutExpired:
            return {"ok": False, "out": "Timeout (exécution stoppée)"}
