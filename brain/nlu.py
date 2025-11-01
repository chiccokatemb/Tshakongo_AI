
import re
INTENTS = {
    "home_light_on":[r"\b(allume|allumer)\b.*\b(lumiere|lumière|lampe)\b"],
    "home_light_off":[r"\b(eteins|éteins|eteindre|éteindre)\b.*\b(lumiere|lumière|lampe)\b"],
    "drive_forward":[r"\b(avance|va tout droit)\b"],
    "drive_stop":[r"\b(stop|arr(ê|e)te)\b"],
    "fs_mkdir":[r"\b(cr(é|e)e|creer|créer) (un )?dossier\b"],
    "script_create":[r"\b(cr(é|e)e|creer|créer) (un )?script\b"],
    "script_run":[r"\b(ex(é|e)cute|lance|run)\b.*\bscript\b"],
    "home_door_open":[r"\b(ouvre|ouvrir) la porte\b"],
    "home_door_close":[r"\b(ferme|fermer) la porte\b"],
    "scene_night":[r"\b(mode nuit|bonne nuit)\b"],
    "scene_party":[r"\b(mode f(ê|e)te|f(ê|e)te)\b"],
    "nav_autonomous_on":[r"\b(passe en autonome|mode autonome|patrouille)\b"],
    "nav_autonomous_off":[r"\b(arr(ê|e)te la patrouille|stop autonome)\b"],
}
def match_intent(text:str)->str:
    t=text.lower()
    for name,pats in INTENTS.items():
        if any(re.search(p,t) for p in pats): return name
    return "freeform"
