import sys
import time

import cv2
import imagehash
import torch
from app.engine import Action, Engine
from app.storage import Metadata
from PIL import Image


class Watcher:
    def __init__(self):
        self.detection_model = self.__init_detection_model()
        self.engine = Engine()
        self.phashes = []

    def run(self, cap_from):
        cap = cv2.VideoCapture(cap_from)

        while cap.isOpened():
            ret, img = cap.read()

            if not ret:
                break

            dets = self.detection_model(img)

            t = time.time()

            for i, d in enumerate(dets.xyxy[0]):
                x1, y1, x2, y2, conf, label = d
                x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

                face = img[y1:y2, x1:x2].copy()

                cv2.rectangle(img,
                              pt1=(x1, y1),
                              pt2=(x2, y2),
                              thickness=2,
                              color=(255, 0, 0),
                              lineType=cv2.LINE_AA)

                is_dup = self.__is_dup(Image.fromarray(face))
                text = "Already detected" if is_dup else f"{dets.names[int(d[-1])]}, confidence={conf:.3f}"
                cv2.putText(img, text, (50, 50 + 50 * i),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                            cv2.LINE_AA)

                if is_dup:
                    continue

                filename = f"./photos/{label}{i}_{t}.jpg"
                cv2.imwrite(filename, face)
                meta = Metadata(filename, '', '',
                                {'username': 'kisasexypantera94'})

                k_nbrs = self.engine.search(meta, Action.LOST)
                if len(k_nbrs) > 0 and k_nbrs[0][0] < 0.5:
                    print("Already in")
                else:
                    self.engine.add(meta, Action.FOUND)

            cv2.imshow('result', img)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()

    def __init_detection_model(self):
        model = torch.hub.load('ultralytics/yolov5',
                               'custom',
                               path='models/yolov5s_805_scratch.pt')
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        return model

    def __is_dup(self, img, threshold=24):
        h = imagehash.phash(img)
        for ph in self.phashes:
            if ph - h < threshold:
                print("Already in: ", ph - h)
                return True
        self.phashes.append(h)
        return False


if __name__ == "__main__":
    cap_from = sys.argv[1] if len(sys.argv) > 1 else 0

    watcher = Watcher()
    watcher.run(cap_from)
