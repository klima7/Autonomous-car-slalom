from enum import Enum
from control import *
import time

class Action(Enum):
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_FORWARD = "go_forward"
    GO_BACK = "go_back"
    STOP = "stop"
    PASS_LEFT ="pass_left"
    PASS_RIGHT="pass_right"


class Movement:

    lastDirection = Action.TURN_LEFT
    AVOID_DISTANCE = 50
    AVOID_DISTANCE_DETECTED_MAX = 60
    AVOID_DISTANCE_DETECTED_MIN = 30
    SIDE_SENSORS_DISTANCE_BIAS = 30

    def move(self, position, classID):
        action = self._get_action(position, classID)

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

        # Back
        elif action == Action.GO_BACK:
            if self.lastDirection in [Action.GO_FORWARD, Action.TURN_LEFT, Action.TURN_RIGHT]:
                stop()
                time.sleep(0.2)
            go_back()

        # Pass right
        elif action == Action.PASS_RIGHT:
            self.pass_right()

        # Pass left
        elif action == Action.PASS_LEFT:
            self.pass_left()

        # Update last
        self.lastDirection = action

    def _get_action(self, position, classID):
        if position:
            return self._get_detected_action(position, classID)
        else:
            return self._get_not_detected_action()


    def _get_detected_action(self, position, classID):
        if position < -25:
            return Action.TURN_LEFT
        elif position > 25:
            return Action.TURN_RIGHT
        elif -25 < position < 25:
            distance = get_distances()[1]
            print(f"Distance: {distance}")
            if distance > 80:
                return self.lastDirection 
            if self.AVOID_DISTANCE_DETECTED_MIN < distance < self.AVOID_DISTANCE_DETECTED_MAX and distance != 0:
                if classID == 1:
                    return Action.PASS_LEFT
                else:
                    return Action.PASS_RIGHT
            elif distance < self.AVOID_DISTANCE_DETECTED_MIN:
                return Action.GO_BACK
            return Action.GO_FORWARD

    def _get_not_detected_action(self):
        distances = get_distances()

        l = distances[0] if distances[0] < self.AVOID_DISTANCE + self.SIDE_SENSORS_DISTANCE_BIAS else 0
        c = distances[1] if distances[0] < self.AVOID_DISTANCE else 0
        r = distances[2] if distances[2] < self.AVOID_DISTANCE + self.SIDE_SENSORS_DISTANCE_BIAS else 0

        if c != 0:
            if r != 0 and l != 0:
                if l < r:
                    return Action.TURN_RIGHT
                elif r < l:
                    return Action.TURN_LEFT
                else:
                    return Action.STOP
            elif r != 0 or l != 0:
                if r == 0:
                    return Action.TURN_RIGHT
                elif l == 0:
                    return Action.TURN_LEFT
            else:
                return self.lastDirection
        elif r != 0:
            return Action.TURN_LEFT
        elif l != 0:
            return Action.TURN_RIGHT
        else:
            return Action.GO_FORWARD

    def pass_right(self):
        forward_time = 2.75
        second_forward_time = 3
        turn_time = 1.5
        second_turn_time = 3
        stop_time = 0.2

        stop()
        time.sleep(stop_time)

        turn_right()
        time.sleep(turn_time)

        start()
        time.sleep(forward_time)

        stop()
        time.sleep(stop_time)

        turn_left()
        time.sleep(second_turn_time)

        start()
        time.sleep(second_forward_time)

        stop()
        time.sleep(stop_time)

        turn_right()
        time.sleep(turn_time)

        stop()

    def pass_left(self):
        forward_time = 2.75
        second_forward_time = 3
        turn_time = 1.5
        second_turn_time = 3
        stop_time = 0.2

        stop()
        time.sleep(stop_time)

        turn_left()
        time.sleep(turn_time)

        start()
        time.sleep(forward_time)

        stop()
        time.sleep(stop_time)

        turn_right()
        time.sleep(second_turn_time)

        start()
        time.sleep(second_forward_time)

        stop()
        time.sleep(stop_time)

        turn_left()
        time.sleep(turn_time)

        stop()