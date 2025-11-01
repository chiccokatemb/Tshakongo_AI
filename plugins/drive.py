
import serial, time, os
class Drive:
    def __init__(self, port:str, baud:int=115200):
        self.enabled = os.path.exists(port)
        if self.enabled:
            self.ser = serial.Serial(port, baudrate=baud, timeout=0.1)
            time.sleep(1.5)
    def _send(self, cmd:str):
        if self.enabled:
            self.ser.write((cmd.strip()+"\n").encode())
    def forward(self, speed:float=0.25): self._send(f"F:{speed:.2f}")
    def stop(self): self._send("S")
