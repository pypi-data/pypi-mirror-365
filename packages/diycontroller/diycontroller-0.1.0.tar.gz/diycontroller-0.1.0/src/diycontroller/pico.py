# This micropython and is intended to run on a Raspberry Pi Pico, you can run it by copying pico.py to the Pico

import network
import socket
import time
from machine import UART

# WiFi credentials
SSID = ''
PASSWORD = ''

# Laptop IP and port
LAPTOP_IP = '192.168.0.79'
LAPTOP_PORT = 5005

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    time.sleep(0.5)

# Set up UART
uart = UART(0, baudrate=115200, tx=0, rx=1)

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    if uart.any():
        line = uart.readline()
        if line:
            print(line)
            sock.sendto(line, (LAPTOP_IP, LAPTOP_PORT))
    time.sleep(0.05)

