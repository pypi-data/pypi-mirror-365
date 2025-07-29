# This code is intended to run on a BBC micro:bit, you can run it by simply copying accelerometer.hex to the micro:bit
#from microbit import *

uart.init(baudrate=115200, tx=pin1, rx=pin0)

while True:
    display.show(Image.HEART)
    sleep(400)

    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()
    uart.write("{},{},{}\n".format(x, y, z))
    sleep(100)
