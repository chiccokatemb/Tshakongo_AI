
# Tshakongo_AI — Option E (Complet)

Assistant vocal **100% local** pour Raspberry Pi :
- 🎙️ Wake-word **tshakongo**, STT (Vosk), TTS (Piper)
- 🧠 Neurone local (llama.cpp / Ollama) + cache sémantique
- 💬 Dialogue → actions (MQTT, robot, fichiers, scripts, nav)
- 🧭 Navigation autonome (LiDAR LD06) simple évitement
- 🛡️ Vision sécurité (armes/chiens) + snapshots + MQTT alert
- 📜 Scripts & Apps (Flask/FastAPI/CLI) + multi-lang (Docker)
- ⏱️ Scheduler (APScheduler)
- 🔁 Mise à jour GitHub

## Démarrage
```bash
cd ~/Tshakongo_AI
bash scripts/manage.sh setup
bash scripts/manage.sh run
# UI: http://<IP_DU_PI>:8080/
```

## Wake-word & Voix
Dans `app/config.yaml` :
```yaml
speech:
  wakeword: "tshakongo"
  wakeword_sensitivity: 0.70
  stt_model_url: "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
  stt_model_dir: "models/vosk-fr"
  tts_voice: "fr"
```
Installe:
```bash
pip install openwakeword onnxruntime numpy sounddevice
sudo apt install piper
```

## MQTT aliases (exemples)
```yaml
mqtt:
  aliases:
    lumiere_salon: "homeassistant/light/salon/set"
    door_main: "homeassistant/lock/porte/set"
    scene_night: "homeassistant/scene/night/set"
    scene_party: "homeassistant/scene/party/set"
```

## Vision sécurité — modèles ONNX
Place des modèles YOLO export ONNX (armes/chiens) et configure si besoin dans le code (`VisionSecure`).  
Captures: `/home/pi/tshakongo/alerts/` — MQTT: `tshakongo/alerts`.

## Nav autonome
- `/api/nav/autonomous/start|stop` — simple évitement (min distance)

## Code multi-langages
`POST /api/code/run` avec `{language, code, args, network}`

## Mise à jour
Bouton UI **Mise à jour** ou `bash scripts/manage.sh update`
