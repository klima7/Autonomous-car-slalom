# sudo systemctl restart nvargus-daemon
import cv2
import numpy as np
from imutils.video import JetsonVideoStream
import jetson.inference
import jetson.utils
import time
from control import init_movement
from movement import movement

modelPath = './net.onnx'
labelsPath = './labels.txt'

frameResolution = (848, 480)
vs = JetsonVideoStream(outputResolution=frameResolution)
vs.start()

runHeadless = False

net = jetson.inference.detectNet(argv=['--model={}'.format(modelPath),
                                       '--labels={}'.format(labelsPath),
                                       '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'],  # , '--input-flip=rotate-180'],
                                 threshold=0.3)

def main():
    init_movement()
    time.sleep(2.0)

    while True:
        image_processing()
        movement()

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    vs.stop()

def image_processing():
    # capture the next image
    frame = vs.read()
    height, width = frame.shape[0:2]

    # convert to CUDA image
    img = frame.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA).astype(np.float32)
    img = jetson.utils.cudaFromNumpy(frame)

    detections = net.Detect(img, width, height)

    print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        x1, y1, x2, y2 = (int(detection.Left), int(detection.Top), int(
            detection.Right), int(detection.Bottom))
        classID = detection.ClassID
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), thickness=3)
        labelX = int((x1+x2)/2)
        labelY = int((y1+y2)/2)
        cv2.putText(frame, str(detection.ClassID), (labelX, labelY),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # print(dir(detection))

    net.PrintProfilerTimes()

    if runHeadless is False:
        cv2.imshow("video", frame)

if __name__ == '__main__':
    main()
