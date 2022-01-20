import serial
import threading
import sys

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)
distances = [0, 0, 0]
theta = 0

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

def turn_right_faster():
    packet = '<turn_right_faster, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def turn_left_faster():
    packet = '<turn_left_faster, 0, 0>'
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

def reset_angle():
    packet = '<reset_angle, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')
    ser.write(packetBytes)

def get_distances():
    return distances

def get_theta():
    return theta

def recieve_data():
    global distances
    global theta
    while True:
        d = ser.read_all()
        if d!=b'':
            try:
                s = d.decode("utf-8")
                last_open = s.rfind("<")
                last_close = s.rfind(">")
                content = s[last_open+1:last_close]
                parts = content.split(",")
                distances = [int(part) for part in parts[0:3]]
                theta = float(parts[3])
            except:
                print('Error')


def init_movement():
    threading.Thread(target = recieve_data).start()
