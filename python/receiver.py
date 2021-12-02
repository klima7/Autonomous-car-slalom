import time
import serial
import threading

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
time.sleep(2.0)
distance = 0
stopped = False
startStopped = False

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

def recieve_data():
    global distance
    while True:
        d = ser.read_all()
        if d!=b'':
            s = d.decode("utf-8")
            last_open = s.rfind("<")
            last_close = s.rfind(">")
            distance = int(s[last_open+1:last_close])
            print(distance)




th = threading.Thread(target = recieve_data)
th.start()
while True:
    if distance == 0:
        if not startStopped:
            stop()
            time.sleep(0.5)
            start()
            stopped = False
            startStopped = True
    else:
        if not stopped:
            stop()
            time.sleep(1.0)
            turn_right()
            stopped=True
            startStopped = False