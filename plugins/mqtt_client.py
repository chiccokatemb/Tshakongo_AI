
import json
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, host:str, port:int=1883, username:str="", password:str=""):
        self.client = mqtt.Client("tshakongo")
        if username or password:
            self.client.username_pw_set(username, password)
        self.client.connect(host, port, 60)
        self.client.loop_start()
    def publish_json(self, topic:str, payload:dict, qos:int=1, retain:bool=False):
        self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
    def publish_state(self, topic:str, on:bool):
        self.publish_json(topic, {"state": "ON" if on else "OFF"})
