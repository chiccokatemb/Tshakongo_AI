
from brain.nlu import match_intent
from speech.tts import speak
def handle_text(text:str, ctx)->str:
    intent = match_intent(text)
    say = lambda m: (speak(m) if ctx.get("use_tts") else None, m)[1]
    if intent == "home_light_on":
        topic = ctx["aliases"].get("lumiere_salon")
        if topic: ctx["mqtt"].publish_state(topic, True); return say("J'allume la lumière du salon.")
        return say("Je ne connais pas la lumière demandée.")
    if intent == "home_light_off":
        topic = ctx["aliases"].get("lumiere_salon")
        if topic: ctx["mqtt"].publish_state(topic, False); return say("J'éteins la lumière du salon.")
        return say("Je ne connais pas la lumière demandée.")
    if intent == "drive_forward":
        msg = ctx["nav"].tick(); return say("J'avance." if not msg else msg)
    if intent == "drive_stop":
        ctx["drive"].stop(); return say("Arrêt.")
    if intent == "fs_mkdir":
        return say(ctx["fs"].mkdir("/home/pi/tshakongo/logs"))
    if intent == "script_create":
        code="print('Bonjour, je suis un script généré !')\n"; return say(ctx["scripts_mgr"].create("auto_demo.py", code))
    if intent == "script_run":
        res = ctx["scripts_mgr"].run_docker("auto_demo.py"); 
        if not res["ok"]: return say("Échec: "+res["out"])
        return say("Sortie: "+res["out"])
    # HA scenes / door
    if intent == "home_door_open":
        topic = ctx["aliases"].get("door_main"); 
        if topic: ctx["mqtt"].publish_state(topic, True); return say("J'ouvre la porte.")
        return say("Je ne trouve pas la porte.")
    if intent == "home_door_close":
        topic = ctx["aliases"].get("door_main"); 
        if topic: ctx["mqtt"].publish_state(topic, False); return say("Je ferme la porte.")
        return say("Je ne trouve pas la porte.")
    if intent == "scene_night":
        topic = ctx["aliases"].get("scene_night"); 
        if topic: ctx["mqtt"].publish_json(topic, {"activate": True}); return say("Mode nuit activé.")
        return say("Scène nuit non configurée.")
    if intent == "scene_party":
        topic = ctx["aliases"].get("scene_party"); 
        if topic: ctx["mqtt"].publish_json(topic, {"activate": True}); return say("Mode fête activé.")
        return say("Scène fête non configurée.")
    # Nav autonomous
    if intent == "nav_autonomous_on":
        if ctx.get("nav_start"): ctx["nav_start"](); return say("Patrouille autonome démarrée.")
        return say("Navigation indisponible.")
    if intent == "nav_autonomous_off":
        if ctx.get("nav_stop"): ctx["nav_stop"](); return say("Patrouille arrêtée.")
        return say("Navigation indisponible.")
    # Freeform → LLM / neuro
    if ctx.get("use_ollama"):
        try: return say(ctx["ollama"](f"Réponds brièvement en français: {text}"))
        except Exception: pass
    if ctx.get("neuro"):
        try: return say(ctx["neuro"].answer(f"Réponds brièvement en français: {text}"))
        except Exception: pass
    return say("Tu as dit: "+text)
