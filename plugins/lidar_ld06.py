
import serial, os, struct

class LD06:
    def __init__(self, port:str, baud:int=230400):
        self.enabled = os.path.exists(port)
        self.buf = bytearray()
        if self.enabled:
            self.s = serial.Serial(port, baudrate=baud, timeout=0.02)

    def _read(self):
        if not self.enabled: return b""
        try: return self.s.read(512)
        except Exception: return b""

    def min_distance(self):
        if not self.enabled:
            return 0.8
        self.buf += self._read()
        # LD06 frames start with 0x54 0x2C and have length 47 bytes typically
        # For simplicity, scan buffer; this is a naive parser (improve as needed)
        while len(self.buf) >= 47:
            idx = self.buf.find(b'\x54\x2C')
            if idx < 0:
                self.buf = self.buf[-46:]; break
            if len(self.buf) - idx < 47: break
            frame = self.buf[idx:idx+47]
            # distances are 12 points 2 bytes each starting at offset 10 (depends on variant)
            dists = []
            for i in range(12):
                off = 10 + i*3  # rough; many LD06 use 3 bytes per point (angle delta, dist LSB, MSB) – simplified
                if off+2 < len(frame):
                    dist = frame[off+1] << 8 | frame[off]
                    if 1 < dist < 6000:
                        dists.append(dist/1000.0)
            self.buf = self.buf[idx+47:]
            if dists:
                return min(dists)
        return 0.8
