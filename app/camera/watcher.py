import cv2
import torch

model = torch.hub.load('ultralytics/yolov5',
                       'custom', force_reload=True,
                       path='models/yolov5s_955_scratch.pt')

# model = torch.hub.load('ultralytics/yolov5',
#                        'yolov5s',
#                        pretrained=True)
model.eval()
for p in model.parameters():
    p.requires_grad = False

cap = cv2.VideoCapture(
    'udpsrc port=5000 caps = "application/x-rtp, media=(string)video, \
        clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" \
            ! rtph264depay ! decodebin ! videoconvert ! appsink',
    cv2.CAP_GSTREAMER)

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

        cv2.putText(img_result,
                    f"{dets.names[int(d[-1])]}, confidence={conf:.3f}",
                    (50, 50 + 50 * i), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('result', img_result)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
