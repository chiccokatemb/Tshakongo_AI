
import cv2, os, time
class Vision:
    def __init__(self):
        self.face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.enabled = False
    def toggle(self, state:bool=None):
        if state is None: self.enabled = not self.enabled
        else: self.enabled = bool(state)
        return self.enabled
    def process(self, frame):
        if not self.enabled or frame is None: return frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face.detectMultiScale(gray, 1.2, 5, minSize=(60,60))
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        return frame

from .detect import Detector
class VisionSecure(Vision):
    def __init__(self, weapon_model=None, dog_model=None, mqtt=None, tts=None):
        super().__init__()
        self.det_weapons = Detector(weapon_model, score_th=0.4)
        self.det_dogs = Detector(dog_model, score_th=0.35)
        self.mqtt, self.tts = mqtt, tts
        self.alert_dir = "/home/pi/tshakongo/alerts"; os.makedirs(self.alert_dir, exist_ok=True)
    def process(self, frame):
        frame = super().process(frame)
        if not self.enabled or frame is None: return frame
        alert=False
        if self.det_weapons.enabled:
            for d in self.det_weapons.infer(frame):
                x1,y1,x2,y2 = d["xyxy"]; cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2); alert=True
        if self.det_dogs.enabled:
            for d in self.det_dogs.infer(frame):
                x1,y1,x2,y2 = d["xyxy"]; cv2.rectangle(frame,(x1,y1),(x2,y2),(0,165,255),2); alert=True
        if alert:
            path = os.path.join(self.alert_dir, f"danger_{int(time.time())}.jpg"); cv2.imwrite(path, frame)
            if self.tts:
                try: self.tts("Alerte sécurité détectée.")
                except Exception: pass
            if self.mqtt:
                try: self.mqtt.publish_json("tshakongo/alerts", {"event":"danger","path":path})
                except Exception: pass
        return frame
