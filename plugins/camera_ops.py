
import cv2, threading
class CameraStreamer:
    def __init__(self, device=0, width=640, height=480):
        self.cap = cv2.VideoCapture(device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.lock = threading.Lock()
    def set_processor(self, fn):
        self._processor = fn
    def _apply(self, frame):
        try:
            if hasattr(self, "_processor") and callable(self._processor):
                return self._processor(frame)
        except Exception:
            pass
        return frame
    def get_frame(self):
        with self.lock:
            ok, frame = self.cap.read()
        if not ok: return None
        frame = self._apply(frame)
        ok, jpg = cv2.imencode(".jpg", frame)
        return jpg.tobytes() if ok else None
