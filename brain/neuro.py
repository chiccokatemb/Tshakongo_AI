
import requests, time
from rapidfuzz import fuzz
class NeuroCache:
    def __init__(self, size=64, threshold=85): self.size=size; self.th=threshold; self.items=[]
    def get(self, q):
        best=None; score=0
        for (qq,aa,ts) in self.items:
            s=fuzz.QRatio(q,qq)
            if s>score: score,best=s,(qq,aa,ts)
        if best and score>=self.th: return best[1],score
        return None,0
    def put(self, q, a):
        self.items.append((q,a,time.time()))
        if len(self.items)>self.size: self.items.pop(0)
class Neuro:
    def __init__(self, cfg:dict):
        self.cfg=cfg or {}; cc=self.cfg.get("cache",{})
        self.cache=NeuroCache(size=int(cc.get("size",64)), threshold=int(cc.get("similarity",85))) if cc.get("enabled",True) else None
    def _llama_cpp_complete(self, prompt:str)->str:
        base=self.cfg.get("llama_server_url","http://127.0.0.1:8081"); url=f"{base}/completion"
        pl={"prompt":prompt,"n_predict":int(self.cfg.get("max_tokens",128)),"temperature":float(self.cfg.get("temperature",0.6)),"cache_prompt":True}
        r=requests.post(url, json=pl, timeout=20); r.raise_for_status(); j=r.json()
        return j.get("content","").strip() or j.get("completion","").strip()
    def _ollama(self, prompt:str)->str:
        host="http://127.0.0.1:11434"; data={"model": self.cfg.get("model","mistral"), "prompt": prompt}
        out=""
        with requests.post(f"{host}/api/generate", json=data, stream=True, timeout=20) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line: continue
                try:
                    import json; j=json.loads(line.decode()); out+=j.get("response","")
                except Exception: pass
        return out.strip()
    def answer(self, prompt:str)->str:
        if self.cache:
            cached,_=self.cache.get(prompt)
            if cached: return cached
        prov=(self.cfg.get("provider") or "llama_cpp").lower()
        try:
            ans=self._ollama(prompt) if prov=="ollama" else self._llama_cpp_complete(prompt)
        except Exception as e:
            ans=f"(neuro offline) {e}"
        if self.cache and ans: self.cache.put(prompt, ans)
        return ans
