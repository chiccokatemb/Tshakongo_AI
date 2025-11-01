
import os, cv2, numpy as np
try:
    import onnxruntime as ort
    HAVE_ORT=True
except Exception:
    HAVE_ORT=False

class Detector:
    def __init__(self, model_path:str=None, score_th=0.35, iou_th=0.45, size=640):
        self.enabled=False; self.size=size; self.score_th=score_th; self.iou_th=iou_th
        if model_path and HAVE_ORT and os.path.exists(model_path):
            try:
                self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider']); self.enabled=True
            except Exception: self.enabled=False
    def _pre(self, img):
        h,w = img.shape[:2]; r=self.size/max(h,w); nh,nw=int(h*r), int(w*r)
        pad=((self.size-nh)//2, (self.size-nw)//2); canvas=np.full((self.size,self.size,3),114,np.uint8)
        canvas[pad[0]:pad[0]+nh, pad[1]:pad[1]+nw] = cv2.resize(img,(nw,nh))
        blob = canvas.transpose(2,0,1)[None].astype(np.float32)/255.0
        return blob, r, pad
    def _nms(self, boxes, scores):
        keep=[]; idx=np.argsort(scores)[::-1]
        while len(idx):
            i=idx[0]; keep.append(i)
            if len(idx)==1: break
            rest=idx[1:]
            xx1=np.maximum(boxes[i,0],boxes[rest,0]); yy1=np.maximum(boxes[i,1],boxes[rest,1])
            xx2=np.minimum(boxes[i,2],boxes[rest,2]); yy2=np.minimum(boxes[i,3],boxes[rest,3])
            w=np.maximum(0,xx2-xx1); h=np.maximum(0,yy2-yy1)
            inter=w*h
            iou=inter/((boxes[i,2]-boxes[i,0])*(boxes[i,3]-boxes[i,1]) + (boxes[rest,2]-boxes[rest,0])*(boxes[rest,3]-boxes[rest,1]) - inter + 1e-6)
            idx=rest[iou<self.iou_th]
        return keep
    def infer(self, img):
        if not self.enabled: return []
        blob, r, pad = self._pre(img)
        out = self.session.run(None, {self.session.get_inputs()[0].name: blob})[0][0]
        boxes = out[:,:4]; obj = out[:,4:5]; cls=out[:,5:]
        scores = obj * cls.max(1, keepdims=True)[0]; cids=cls.argmax(1)
        mask = (scores[:,0] > self.score_th)
        boxes,scores,cids = boxes[mask],scores[mask,0],cids[mask]
        xyxy = np.zeros_like(boxes)
        xyxy[:,0] = (boxes[:,0]-boxes[:,2]/2 - pad[1]) / r
        xyxy[:,1] = (boxes[:,1]-boxes[:,3]/2 - pad[0]) / r
        xyxy[:,2] = (boxes[:,0]+boxes[:,2]/2 - pad[1]) / r
        xyxy[:,3] = (boxes[:,1]+boxes[:,3]/2 - pad[0]) / r
        h,w = img.shape[:2]
        xyxy[:,[0,2]] = np.clip(xyxy[:,[0,2]],0,w-1); xyxy[:,[1,3]] = np.clip(xyxy[:,[1,3]],0,h-1)
        keep = self._nms(xyxy, scores)
        return [{"xyxy": tuple(map(int, xyxy[i])), "score": float(scores[i]), "cls": int(cids[i])} for i in keep]
