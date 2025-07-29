# diyController

This project enables mouse control using a micro:bit and a Raspberry Pi Pico, transmitting accelerometer data over WiFi to a laptop, which interprets the data as mouse movements.

## How It Works

1. **Micro:bit**
	- Reads accelerometer data (X, Y, Z axes).
	- Sends data via serial to the Raspberry Pi Pico, over pins 0 and 1.

2. **Raspberry Pi Pico**
	- Receives accelerometer data from the micro:bit over GP0 and GP1.
	- Connects to WiFi and transmits the data to the laptop using a network protocol (e.g., UDP/TCP/WebSocket).

3. **Laptop**
	- Runs a script or application that listens for incoming data from the Pico.
	- Interprets the accelerometer data to move the mouse cursor accordingly.

## Setup

1. **Micro:bit**s
	- Flash code to read and send accelerometer data.

2. **Raspberry Pi Pico**
	- Connect to WiFi.
	- Flash code to receive data from micro:bit and send it to the laptop.

3. **Laptop**
	- Run a listener script (e.g., Python) to receive data and control the mouse.

## Requirements

- BBC micro:bit
- Raspberry Pi Pico with WiFi (e.g., Pico W)
- Laptop (Windows, macOS, or Linux)
- Micro USB cables
- Python (for laptop listener script)
- Required libraries: `pyserial`, `pynput`, `socket`

## Example Workflow

1. Move the micro:bit to generate accelerometer data.
2. Data is sent to the Pico, which forwards it over WiFi.
3. The laptop receives the data and moves the mouse cursor based on the accelerometer readings.

