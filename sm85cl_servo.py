#!/usr/bin/env python3

import time
import pyautogui
from scservo_sdk import *


# ================= CONFIG =================

PORT = "/dev/ttyUSB0"     # change if needed
BAUD = 115200

SERVO_ID = 1


# SMS/STS register addresses

ADDR_TORQUE = 40
ADDR_GOAL_POSITION = 42
ADDR_GOAL_SPEED = 46
ADDR_GOAL_ACC = 41


# servo range
SERVO_MAX = 4095


SPEED = 3000
ACC = 50


# ==========================================


screen_w, screen_h = pyautogui.size()


portHandler = PortHandler(PORT)
packetHandler = PacketHandler(0)


if not portHandler.openPort():
    print("Failed opening port")
    quit()


if not portHandler.setBaudRate(BAUD):
    print("Failed baudrate")
    quit()


print("Connected")


# enable torque

packetHandler.write1ByteTxRx(
    portHandler,
    SERVO_ID,
    ADDR_TORQUE,
    1
)


print("Move mouse X axis")


while True:


    x, y = pyautogui.position()


    # map screen X -> 0-180 degrees

    angle = (x/screen_w)*180


    # SM85CL 0-360 = 0-4095
    # therefore 0-180 = 0-2047

    position = int(
        angle/360*SERVO_MAX
    )


    # write position

    packetHandler.write2ByteTxRx(
        portHandler,
        SERVO_ID,
        ADDR_GOAL_POSITION,
        position
    )


    # write speed

    packetHandler.write2ByteTxRx(
        portHandler,
        SERVO_ID,
        ADDR_GOAL_SPEED,
        SPEED
    )


    print(
        "angle:",
        round(angle,1),
        "pos:",
        position
    )


    time.sleep(0.02)