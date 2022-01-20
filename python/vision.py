import cv2
import numpy as np
import jetson.inference
import jetson.utils
from imutils.video import JetsonVideoStream


modelPath = './net.onnx'
labelsPath = './labels.txt'

frameResolution = (848, 480)
vs = JetsonVideoStream(outputResolution=frameResolution)

runHeadless = False

net = jetson.inference.detectNet(argv=['--model={}'.format(modelPath),
                                       '--labels={}'.format(labelsPath),
                                       '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'],  # , '--input-flip=rotate-180'],
                                 threshold=0.3)

def init():
    vs.start()


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

    # print("detected {:d} objects in image".format(len(detections)))

    for detection in detections:
        x1, y1, x2, y2 = (int(detection.Left), int(detection.Top), int(
            detection.Right), int(detection.Bottom))
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), thickness=3)
        labelX = int((x1+x2)/2)
        labelY = int((y1+y2)/2)
        cv2.putText(frame, str(detection.ClassID), (labelX, labelY),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    detectionsWithHeight = ((detection, detection.Top-detection.Bottom) for detection in detections)
    sortedDetections = sorted(detectionsWithHeight, key=lambda x: x[1])
    position = None
    classID = None
    if sortedDetections:
        d = sortedDetections[0][0]
        classID = d.ClassID
        labelX = int((d.Left+d.Right)/2)
        labelY = int((d.Bottom+d.Top)/2)-20
        position = labelX - (frameResolution[0] / 2)
        cv2.putText(frame, f'Nearest ({position})', (labelX, labelY),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # net.PrintProfilerTimes()

    if runHeadless is False:
        cv2.imshow("video", frame)

    return position, classID


def dispose():
    vs.stop()