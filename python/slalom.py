# sudo systemctl restart nvargus-daemon
import cv2
import numpy as np
import jetson.inference
import jetson.utils
import time
from control import init_movement
from movement import Movement
import vision


def main():
    vision.init()
    init_movement()
    time.sleep(2.0)
    movement = Movement()

    while True:
        position, classID = vision.image_processing()
        movement.move(position, classID)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    vision.dispose()


if __name__ == '__main__':
    main()
