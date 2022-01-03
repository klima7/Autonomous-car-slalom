import serial
import threading

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
distances = [0, 0, 0]

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

def go_back():
    packet = '<go_back, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def pass_left():
    packet = '<pass_left, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def pass_right():
    packet = '<pass_right, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def get_distances():
    return distances

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

def init_movement():
    threading.Thread(target = recieve_data).start()
