"""
Découverte basique MQTT (Home Assistant) :
- S'abonne à homeassistant/#
- Liste entités (light, lock, scene) -> propose aliases
Usage: à lancer depuis le Pi; UI à relier côté app plus tard.
"""
import paho.mqtt.client as mqtt
import time, json

class HADiscovery:
    def __init__(self, host="127.0.0.1", port=1883, timeout=4):
        self.host, self.port = host, port
        self.topics = []
        self.client = mqtt.Client("tsk_discovery")
        self.client.on_message = self._on_msg

    def _on_msg(self, _c, _u, msg):
        t = msg.topic
        if any(t.startswith(p) for p in ("homeassistant/light", "homeassistant/lock", "homeassistant/scene")):
            if t not in self.topics:
                self.topics.append(t)

    def run(self):
        self.client.connect(self.host, self.port, 60)
        self.client.subscribe("homeassistant/#")
        self.client.loop_start()
        time.sleep(4)
        self.client.loop_stop()
        return self.topics

if __name__ == "__main__":
    d = HADiscovery()
    print(json.dumps(d.run(), indent=2, ensure_ascii=False))
