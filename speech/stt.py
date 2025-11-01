
import os, zipfile, urllib.request, json, queue, sounddevice as sd
from vosk import Model, KaldiRecognizer

def ensure_model(url, model_dir):
    if os.path.isdir(model_dir): return
    os.makedirs("models", exist_ok=True)
    z = "models/model_fr.zip"
    urllib.request.urlretrieve(url, z)
    with zipfile.ZipFile(z) as f: f.extractall("models")
    if not os.path.isdir(model_dir):
        for d in os.listdir("models"):
            if d.startswith("vosk-model") and os.path.isdir(os.path.join("models", d)):
                os.rename(os.path.join("models", d), model_dir); break

class STT:
    def __init__(self, url, model_dir):
        ensure_model(url, model_dir); self.model = Model(model_dir)
    def listen_once(self, seconds=4):
        q = queue.Queue()
        def cb(indata, frames, time, status): q.put(bytes(indata))
        rec = KaldiRecognizer(self.model, 16000)
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=cb):
            chunks = int(seconds*16000/8000)
            for _ in range(chunks):
                data = q.get()
                if rec.AcceptWaveform(data):
                    import json; return json.loads(rec.Result()).get("text","").strip()
        import json; return json.loads(rec.FinalResult()).get("text","").strip()
