# sudo systemctl restart nvargus-daemon
import cv2
import numpy as np
import jetson.inference
import jetson.utils
import time
from control import init_movement
import movement
import vision


def main():
    vision.init()
    init_movement()
    time.sleep(2.0)

    while True:
        position = vision.image_processing()
        movement.move(position)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    vision.dispose()


if __name__ == '__main__':
    main()
