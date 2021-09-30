import sys

import cv2
import torch

model = torch.hub.load('ultralytics/yolov5',
                       'custom',
                       path='models/yolov5s_987.pt')
# model = torch.hub.load('ultralytics/yolov5',
#                        'yolov5s',
#                        pretrained=True)
model.eval()
for p in model.parameters():
    p.requires_grad = False

video_path = sys.argv[1]
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, img = cap.read()

    if not ret:
        break

    img_result = img.copy()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    dets = model(img)

    for i, d in enumerate(dets.xyxy[0]):
        x1, y1, x2, y2, conf, label = d
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        cv2.rectangle(img_result,
                      pt1=(x1, y1),
                      pt2=(x2, y2),
                      thickness=2,
                      color=(255, 0, 0),
                      lineType=cv2.LINE_AA)

        cv2.putText(img_result, dets.names[int(d[-1])], (50, 50 + 50 * i),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    cv2.imshow('result', img_result)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
