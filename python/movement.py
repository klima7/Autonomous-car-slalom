from enum import Enum
from control import *
import time
import math
import random

class Action(Enum):
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_FORWARD = "go_forward"
    GO_BACK = "go_back"
    STOP = "stop"
    PASS_LEFT ="pass_left"
    PASS_RIGHT="pass_right"
    AVOID_LEFT="avoid_left"
    AVOID_RIGHT="avoid_right"


class Movement:

    lastDirection = Action.TURN_LEFT
    AVOID_DISTANCE = 30
    SIDE_SENSORS_DISTANCE_BIAS = 20
    AVOID_DISTANCE_DETECTED_MAX = 60
    AVOID_DISTANCE_DETECTED_MIN = 30

    THRESHOLD_MIN = 60
    THRESHOLD_MAX = 90

    # Passing constants
    forward_time = 2.75
    second_forward_time = 3
    stop_time = 0.2
    first_angle = 30
    second_angle = 60
    third_angle = 20 

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
            turn_left_slower()
            time.sleep(0.1)
            stop()
            time.sleep(0.3)

        # Right
        elif action == Action.TURN_RIGHT:
            if self.lastDirection == Action.TURN_LEFT or self.lastDirection == Action.GO_FORWARD:
                stop()
                time.sleep(0.2)
            turn_right_slower()
            time.sleep(0.1)
            stop()
            time.sleep(0.3)

        # Avoid Left
        elif action == Action.AVOID_LEFT:
            if self.lastDirection == Action.TURN_RIGHT or self.lastDirection == Action.GO_FORWARD:
                stop()
                time.sleep(0.2)
                go_back()
                time.sleep(0.4)
                stop()
                time.sleep(0.2)
            turn_left()
            sleep_time = random.uniform(0.9, 1.8)
            time.sleep(sleep_time)

        # Avoid Right
        elif action == Action.AVOID_RIGHT:
            if self.lastDirection == Action.TURN_LEFT or self.lastDirection == Action.GO_FORWARD:
                stop()
                time.sleep(0.2)
                go_back()
                time.sleep(0.4)
                stop()
                time.sleep(0.2)
            turn_right()
            sleep_time = random.uniform(0.9, 1.8)
            time.sleep(sleep_time)

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
        treshold = self.THRESHOLD_MAX
        max_dist = 80
        dist = get_distances()[1]
        division = ((self.THRESHOLD_MAX -dist)/(max_dist-self.THRESHOLD_MIN))
        print("Distance: ", dist)
        treshold = treshold * division
        treshold = self.THRESHOLD_MIN if treshold < self.THRESHOLD_MIN else treshold

        if position < -treshold:
            return Action.TURN_LEFT
        elif position > treshold:
            return Action.TURN_RIGHT
        elif -treshold < position < treshold:
            distance = get_distances()[1]
            # print(f"Distance: {distance}")
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
                    return Action.AVOID_RIGHT
                elif r < l:
                    return Action.AVOID_LEFT
                else:
                    return Action.STOP
            elif r != 0 or l != 0:
                if r == 0:
                    return Action.AVOID_RIGHT
                elif l == 0:
                    return Action.AVOID_LEFT
            else:
                return self.lastDirection
        elif r != 0:
            return Action.AVOID_LEFT
        elif l != 0:
            return Action.AVOID_RIGHT
        else:
            return Action.GO_FORWARD

    def pass_right(self):
        stop()
        time.sleep(self.stop_time)

        self.turn_exact(self.first_angle)

        start()
        time.sleep(self.forward_time)

        stop()
        time.sleep(self.stop_time)

        self.turn_exact(-self.second_angle)

        start()
        time.sleep(self.second_forward_time)

        stop()
        time.sleep(self.stop_time)

        self.turn_exact(self.third_angle)

    def pass_left(self):
        stop()
        time.sleep(self.stop_time)

        self.turn_exact(-self.first_angle)

        start()
        time.sleep(self.forward_time)

        stop()
        time.sleep(self.stop_time)

        self.turn_exact(self.second_angle)

        start()
        time.sleep(self.second_forward_time)

        stop()
        time.sleep(self.stop_time)

        self.turn_exact(-self.third_angle)

    def turn_exact(self, angle_degree):
        print("Turning")

        angle_degree = angle_degree * 2

        if angle_degree == 0:
            return

        radians = math.radians(angle_degree)
        if radians < 0:
            radians = 2*math.pi + radians

        stop()
        time.sleep(0.5)
        
        reset_angle()
        time.sleep(1)
        print('Theta after reset:', get_theta())

        if(angle_degree < 0):
            turn_left()
            theta = get_theta()
            print('Before theta:', theta, '/', radians)
            while(theta >= radians or theta == 0):
                print('Turn theta:', theta, '/', radians)
                theta = get_theta()
                time.sleep(0.1)
        else:
            turn_right()
            theta = get_theta()
            print('Before theta:', theta, '/', radians)
            while(theta <= radians or theta > 2*math.pi-0.4):
                print('Turn theta:', theta, '/', radians)
                theta = get_theta()
                time.sleep(0.1)
        stop()