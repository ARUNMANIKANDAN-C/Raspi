import serial
import time

# Replace with your actual port (check using `ls /dev/tty*`)
arduino_port = '/dev/ttyACM0'  # or '/dev/ttyUSB0'
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset

    print("Connected to Arduino")

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print("Received:", line)

except serial.SerialException as e:
    print(f"Error: {e}")
