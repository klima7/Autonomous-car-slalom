from enum import Enum
from control import *
import time

class Action(Enum):
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_FORWARD = "go_forward"
    STOP = "stop"


class Movement:

    lastDirection = Action.TURN_LEFT

    def move(self, position):
        global lastDirection
        action = self._get_action(position)

        # Forward
        if action == Action.GO_FORWARD:
            if self.lastDirection == Action.TURN_LEFT or self.lastDirection == Action.TURN_RIGHT:
                stop()
                time.sleep(0.2)
            start()

        # Stop
        elif action == Action.STOP:
            stop()

        # Left
        elif action == Action.TURN_LEFT:
            if self.lastDirection == Action.TURN_RIGHT or self.lastDirection == Action.GO_FORWARD:
                stop()
                time.sleep(0.2)
            turn_left()

        # Right
        elif action == Action.TURN_RIGHT:
            if self.lastDirection == Action.TURN_LEFT or self.lastDirection == Action.GO_FORWARD:
                stop()
                time.sleep(0.2)
            turn_right()

        # Update last
        self.lastDirection = action

    def _get_action(self, position):
        if position:
            return self._get_detected_action(position)
        else:
            return Action.STOP
        # else:
        #     return get_not_detected_action()


    def _get_detected_action(self, position):
        if position < -25:
            return Action.TURN_LEFT
        elif position > 25:
            return Action.TURN_RIGHT
        elif -25 < position < 25:
            return Action.GO_FORWARD


    def _get_not_detected_action(self):
        action = self._get_not_detected_action_temp()
        # if action == Action.TURN_LEFT or action == Action.TURN_RIGHT:
        #     lastDirection = action
        return action

    def _get_not_detected_action_temp(self):
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
                print('Moving in same direction')
                return self.lastDirection
        elif right != 0:
            return Action.TURN_LEFT
        elif left != 0:
            return Action.TURN_RIGHT
        else:
            return Action.GO_FORWARD
