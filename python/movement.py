from enum import Enum
from control import *
import time

class Action(Enum):
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_FORWARD = "go_forward"
    STOP = "stop"

stopped = False
startStopped = False

def movement():
    global stopped
    global startStopped
    action = get_action()
    print('action: ' + str(action))
    if action == Action.GO_FORWARD:
        if not startStopped:
            stop()
            time.sleep(0.4)
            start()
            stopped = False
            startStopped = True
    elif action == Action.STOP:
        stop()
        stopped = True
        startStopped = True
    elif action == Action.TURN_LEFT:
        if not stopped:
            stop()
            time.sleep(0.2)
            turn_left()
            stopped = True
            startStopped = False
    elif action == Action.TURN_RIGHT:
        if not stopped:
            stop()
            time.sleep(0.2)
            turn_right()
            stopped = True
            startStopped = False



def get_action():
    distances = get_distances()

    left = distances[0]
    center = distances[1]
    right = distances[2]
    print(f"{left} {center} {right}")
    if center != 0:
        if right != 0 and left != 0:
            if left < right:
                return Action.TURN_RIGHT
            elif right < left:
                return Action.TURN_LEFT
            else:
                return Action.STOP
        elif right != 0 or left != 0:
            if right == 0:
                return Action.TURN_RIGHT
            elif left == 0:
                return Action.TURN_LEFT
        else:
            return Action.TURN_RIGHT # or left
    elif right != 0:
        return Action.TURN_LEFT
    elif left != 0:
        return Action.TURN_RIGHT
    else:
        return Action.GO_FORWARD