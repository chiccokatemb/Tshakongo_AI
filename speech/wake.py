
try:
    from openwakeword.model import Model as OWWModel
    import sounddevice as sd
    import numpy as np
    HAVE_OWW = True
except Exception:
    HAVE_OWW = False

def wait_hotword(hotword="tshakongo", sensitivity=0.7):
    if not HAVE_OWW:
        input("[PTT] Appuie Entrée pour parler... "); return True
    model = OWWModel(); samplerate = 16000; blocksize = 16000//4
    prob_th = max(0.15, min(0.95, sensitivity))
    def stream():
        with sd.InputStream(channels=1, samplerate=samplerate, blocksize=blocksize, dtype='float32') as s:
            while True: audio,_=s.read(blocksize); yield audio[:,0]
    for chunk in stream():
        pred = model.predict(chunk)
        if any(v>=prob_th for v in pred.values()): return True
