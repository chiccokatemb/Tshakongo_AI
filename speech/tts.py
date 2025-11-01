
import subprocess, tempfile, os
def speak(text:str, lang_code="fr"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav = f.name
    subprocess.run(["piper","-l",lang_code,"-w",wav], input=text.encode(), check=False)
    subprocess.run(["aplay", wav], check=False)
    try: os.remove(wav)
    except Exception: pass
