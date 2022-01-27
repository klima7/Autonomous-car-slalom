import serial
import time

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.05)

def init():
    packet = '<init, 0, 0>'
    packetBytes = bytes(packet, 'utf-8')  
    ser.write(packetBytes)


if __name__ == '__main__':
    time.sleep(2)
    init()
