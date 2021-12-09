import time
import serial
import threading
from enum import Enum

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
time.sleep(2.0)
distances = [0, 0, 0]

stopped = False
startStopped = False

class Action(Enum):
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GO_FORWARD = "go_forward"
    STOP = "stop"

def start():
    packet = '<start, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')  
    ser.write(packetBytes)


def stop():
    packet = '<stop, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')  
    ser.write(packetBytes)

def turn_right():
    packet = '<turn_right, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def turn_left():
    packet = '<turn_left, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def get_action():
    left = distances[0]
    center = distances[1]
    right = distances[2]

    if center != 0:
        if right != 0 and left != 0:
            if left < right:
                return Action.TURN_RIGHT
            elif right < left:
                return Action.TURN_LEFT
            else:
                return Action.STOP
        elif right != 0 or left !=0:
            if right == 0:
                return Action.TURN_RIGHT
            elif left == 0:
                return Action.TURN_LEFT
    elif right != 0:
        return Action.TURN_LEFT
    elif left != 0:
        return Action.TURN_RIGHT
    else:
        return Action.GO_FORWARD

def recieve_data():
    global distances
    while True:
        d = ser.read_all()
        if d!=b'':
            s = d.decode("utf-8")
            last_open = s.rfind("<")
            last_close = s.rfind(">")
            content = s[last_open+1:last_close]
            parts = content.split(",")
            distances = [int(part) for part in parts]


th = threading.Thread(target = recieve_data)
th.start()
while True:
    action = get_action()
    print(action)

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
            stopped=True
            startStopped = False
    elif action == Action.TURN_RIGHT:
        if not stopped:
            stop()
            time.sleep(0.2)
            turn_right()
            stopped=True
            startStopped = False

    # if distance == 0:
    #     if not startStopped:
    #         stop()
    #         time.sleep(0.4)
    #         start()
    #         stopped = False
    #         startStopped = True
    # else:
    #     if not stopped:
    #         stop()
    #         time.sleep(0.2)
    #         turn_right()
    #         stopped=True
    #         startStopped = False