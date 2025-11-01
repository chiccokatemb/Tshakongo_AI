
import json, urllib.request
def ollama_chat(prompt:str, model="mistral", host="http://127.0.0.1:11434", timeout=12):
    data = json.dumps({"model": model, "prompt": prompt}).encode()
    req = urllib.request.Request(f"{host}/api/generate", data=data, headers={"Content-Type":"application/json"})
    out=""
    with urllib.request.urlopen(req, timeout=timeout) as r:
        for line in r:
            j=json.loads(line); out+=j.get("response","")
    return out.strip()
