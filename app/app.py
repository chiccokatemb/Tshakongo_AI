
from flask import Flask, render_template, jsonify, Response, request
from flask_socketio import SocketIO
import yaml, os, subprocess, time

from plugins.fs_ops import FSSandbox
from plugins.drive import Drive
from plugins.lidar_ld06 import LD06
from plugins.nav import SimpleAvoid
from plugins.camera_ops import CameraStreamer
from plugins.mqtt_client import MQTTClient
from plugins.scheduler import JobScheduler
from plugins.scripts_manager import ScriptsManager
from plugins.app_scaffold import scaffold as scaffold_app
from plugins.vision import VisionSecure
from brain.dialogue import handle_text
from brain.llm import ollama_chat
from brain.neuro import Neuro
from speech.stt import STT
from speech.wake import wait_hotword
from speech.tts import speak

BASE_DIR = os.path.dirname(__file__)
CFG = yaml.safe_load(open(os.path.join(BASE_DIR,"config.yaml"),"r"))

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Core services
fs = FSSandbox(CFG["security"]["fs_allowlist"])
drive = Drive(CFG["robot"]["serial_arduino"])
lidar = LD06(CFG["robot"]["lidar_uart"], CFG["robot"]["lidar_baud"])
nav = SimpleAvoid(lidar, drive, CFG["robot"]["stop_dist"], CFG["robot"]["max_speed"])
cam = CameraStreamer(device=0)

MQTT_CFG = CFG.get("mqtt", {})
mqtt_cli = MQTTClient(MQTT_CFG.get("broker","127.0.0.1"), int(MQTT_CFG.get("port",1883)), MQTT_CFG.get("username",""), MQTT_CFG.get("password",""))
aliases = MQTT_CFG.get("aliases", {})

scheduler = JobScheduler()

# Neuro / Dialogue
NEURO = Neuro(CFG.get("neuro", {}))
def dialogue_ctx():
    DCFG = CFG.get("dialogue", {})
    return {
        "drive": drive, "mqtt": mqtt_cli, "fs": fs,
        "scripts_mgr": scripts_mgr if "scripts_mgr" in globals() else None,
        "cfg": CFG, "use_tts": bool(DCFG.get("use_tts", True)),
        "use_ollama": bool(DCFG.get("use_ollama", False)),
        "ollama": lambda p: ollama_chat(p, model=DCFG.get("ollama_model","mistral")),
        "aliases": aliases, "nav": nav,
        "neuro": NEURO, "nav_start": lambda: nav_start(), "nav_stop": lambda: nav_stop(),
    }

# Vision secure
VISION = VisionSecure(mqtt=mqtt_cli, tts=speak)
cam.set_processor(VISION.process)

@app.route("/")
def index(): return render_template("index.html")

# FS
@app.route("/api/fs/mkdir", methods=["POST"])
def api_fs_mkdir():
    path = request.json.get("path"); return jsonify({"msg": fs.mkdir(path)})
@app.route("/api/fs/list", methods=["POST"])
def api_fs_list():
    path = request.json.get("path"); return jsonify({"msg": fs.listdir(path)})

# Robot
@app.route("/api/robot/forward", methods=["POST"])
def api_robot_forward():
    msg = nav.tick(); return jsonify({"msg": msg or "ok"})
@app.route("/api/robot/stop", methods=["POST"])
def api_robot_stop():
    drive.stop(); return jsonify({"msg":"ok"})

# LiDAR
@app.route("/api/lidar/min")
def api_lidar_min():
    d = lidar.min_distance(); return jsonify({"min": d})

# Camera stream
def gen_video():
    while True:
        frame = cam.get_frame()
        if not frame: time.sleep(0.05); continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
@app.route("/video_feed")
def video_feed():
    return Response(gen_video(), mimetype="multipart/x-mixed-replace; boundary=frame")

# Update (git)
@app.route("/api/update", methods=["POST"])
def api_update():
    repo_url = CFG["project"].get("repo_url"); project_root = os.path.abspath(os.path.join(BASE_DIR, ".."))
    if not os.path.exists(os.path.join(project_root, ".git")):
        subprocess.run(["git","init"], cwd=project_root, check=False)
        if repo_url: subprocess.run(["git","remote","add","origin", repo_url], cwd=project_root, check=False)
    out=[]
    def run(cmd):
        p = subprocess.run(cmd, cwd=project_root, text=True, capture_output=True); out.append("$ "+" ".join(cmd)); out.append(p.stdout+p.stderr); return p.returncode
    run(["git","fetch","origin"]); run(["git","pull","origin","principal"]); run(["git","pull","origin","main"])
    msg = "\\n".join(out[-10:]); return jsonify({"msg":"Mise à jour terminée:\\n"+msg})

# Scripts manager
SMCFG = CFG.get("script_sandbox", {})
scripts_mgr = ScriptsManager(
    root_dir=SMCFG.get("root_dir","/home/pi/tshakongo/scripts"),
    docker_image=SMCFG.get("docker_image","python:3.11-slim"),
    network=SMCFG.get("network","none"),
    mem_limit=SMCFG.get("mem_limit","256m"),
    cpus=SMCFG.get("cpus","0.75"),
    timeout_sec=int(SMCFG.get("timeout_sec",25)),
    enable_native=bool(SMCFG.get("enable_native_exec", False)),
)

@app.route("/api/scripts/create", methods=["POST"])
def api_scripts_create():
    data = request.get_json(force=True); name = data.get("name","").strip(); content = data.get("content","")
    return jsonify({"msg": scripts_mgr.create(name, content)})
@app.route("/api/scripts/list")
def api_scripts_list(): return jsonify({"scripts": scripts_mgr.list()})
@app.route("/api/scripts/read", methods=["POST"])
def api_scripts_read():
    name = request.json.get("name",""); content = scripts_mgr.read(name); return jsonify({"content": content})
@app.route("/api/scripts/delete", methods=["POST"])
def api_scripts_delete():
    name = request.json.get("name",""); confirm = bool(request.json.get("confirm", False))
    return jsonify({"msg": scripts_mgr.delete(name, confirm)})
@app.route("/api/scripts/run", methods=["POST"])
def api_scripts_run():
    name = request.json.get("name",""); args = request.json.get("args", []); res = scripts_mgr.run_docker(name, args=args); return jsonify(res)

# Scaffold
@app.route("/api/scaffold", methods=["POST"])
def api_scaffold():
    data = request.get_json(force=True); kind = data.get("kind","flask"); target = data.get("target","/home/pi/tshakongo/apps/sample")
    appname = data.get("app_name","MyApp"); port = int(data.get("port", 5000)); msg = scaffold_app(kind, target, appname, port)
    return jsonify({"msg": msg})

# Dialogue
@app.route("/api/dialogue", methods=["POST"])
def api_dialogue():
    txt = request.json.get("text",""); ctx = dialogue_ctx(); res = handle_text(txt, ctx); return jsonify({"reply": res})

# Voice loop (wake + stt + dialogue + memory)
from brain.memory import Memory
MEM = Memory()
from threading import Thread
VOICE_RUNNING = {"on": False}
STT_ENGINE = STT(CFG["speech"]["stt_model_url"], CFG["speech"]["stt_model_dir"])
def voice_worker():
    speak("Assistant vocal démarré.")
    while VOICE_RUNNING["on"]:
        ok = wait_hotword(CFG["speech"].get("wakeword","tshakongo"), CFG["speech"].get("wakeword_sensitivity",0.7))
        if not ok or not VOICE_RUNNING["on"]: continue
        speak("Je vous écoute.")
        txt = STT_ENGINE.listen_once(seconds=5)
        if not txt: speak("Je n'ai pas entendu."); continue
        res = handle_text(txt, dialogue_ctx()); MEM.log_turn(txt, res)
@app.route("/api/voice/start", methods=["POST"])
def api_voice_start():
    if not VOICE_RUNNING["on"]:
        VOICE_RUNNING["on"] = True; Thread(target=voice_worker, daemon=True).start(); return jsonify({"msg":"Voix ON"})
    return jsonify({"msg":"Déjà en marche"})
@app.route("/api/voice/stop", methods=["POST"])
def api_voice_stop(): VOICE_RUNNING["on"] = False; return jsonify({"msg":"Voix OFF"})

# Memory endpoints
@app.route("/api/memory/set", methods=["POST"])
def api_memory_set():
    k = request.json.get("key"); v = request.json.get("value"); 
    return jsonify({"msg": MEM.set_fact(k, v)})
@app.route("/api/memory/get", methods=["POST"])
def api_memory_get():
    k = request.json.get("key"); return jsonify({"value": MEM.get_fact(k)})
@app.route("/api/memory/all")
def api_memory_all(): return jsonify(MEM.all_facts())
@app.route("/api/memory/history")
def api_memory_history():
    n = int(request.args.get("n", 30)); return jsonify(MEM.history(n))

# Vision toggle
@app.route("/api/vision/toggle", methods=["POST"])
def api_vision_toggle():
    state = request.json.get("state", None); en = VISION.toggle(state if state is not None else None)
    return jsonify({"enabled": en})

# Autonomous nav
NAV_RUNNING = {"on": False}
def nav_worker():
    while NAV_RUNNING["on"]:
        msg = nav.tick(); socketio.emit("nav", {"msg": msg}); time.sleep(0.1)
def nav_start():
    if not NAV_RUNNING["on"]:
        NAV_RUNNING["on"] = True; Thread(target=nav_worker, daemon=True).start()
def nav_stop(): NAV_RUNNING["on"] = False
@app.route("/api/nav/autonomous/start", methods=["POST"])
def api_nav_start(): nav_start(); return jsonify({"msg":"autonome ON"})
@app.route("/api/nav/autonomous/stop", methods=["POST"])
def api_nav_stop(): nav_stop(); return jsonify({"msg":"autonome OFF"})

# Scheduler
@app.route("/api/schedule/minutes", methods=["POST"])
def api_schedule_minutes():
    data = request.get_json(force=True); job_id = data.get("id","job1"); minutes = int(data.get("minutes", 10))
    def run_demo(): scripts_mgr.run_docker("demo.py")
    msg = scheduler.add_every_minutes(job_id, minutes, run_demo); return jsonify({"msg": msg})
@app.route("/api/schedule/cron", methods=["POST"])
def api_schedule_cron():
    data = request.get_json(force=True); job_id = data.get("id","job1"); cron = data.get("cron", {"minute":"0","hour":"8"})
    def run_demo(): scripts_mgr.run_docker("demo.py")
    msg = scheduler.add_cron(job_id, cron, run_demo); return jsonify({"msg": msg})
@app.route("/api/schedule/list")
def api_schedule_list(): return jsonify({"jobs": scheduler.list()})
@app.route("/api/schedule/remove", methods=["POST"])
def api_schedule_remove(): jid = request.json.get("id","job1"); return jsonify({"msg": scheduler.remove(jid)})

# Neuro test
NEURO = Neuro(CFG.get("neuro", {}))
@app.route("/api/neuro/test", methods=["POST"])
def api_neuro_test():
    txt = request.json.get("text","Bonjour ! Présente-toi en une phrase."); out = NEURO.answer(txt); return jsonify({"reply": out})

if __name__ == "__main__":
    socketio.run(app, host=CFG["server"]["host"], port=CFG["server"]["port"])
