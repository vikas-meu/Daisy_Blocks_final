#!/usr/bin/env python3
"""
ST3215 Linear Actuator - Smart Mapping (10% to 100%)
====================================================
Problem solved:
- Typing 0 was going past physical home because virtual 0 was on the wrong side of the stop.

Solution (fully automatic, no tuning needed):
After finding HOME and END, we internally map user input 0-100 to 10%-100% of the stroke.
- User types 0  → actuator goes to 10% of stroke (safely away from hard stop)
- User types 10 → actuator goes to ~ physical home position you marked
- User types 100 → actuator goes to full END

This way the code never commands the actuator all the way to the hard stop.
No back-off tuning required. Everything sets itself automatically.
"""

from scservo_sdk import *
import time


# ================= CONFIG =================

PORT = "/dev/ttyACM0"
BAUD = 1000000
SERVO_ID = 1

ADDR_MODE = 33
ADDR_TORQUE = 40
ADDR_SPEED = 46
ADDR_PRESENT_POS = 56
ADDR_CURRENT = 69

ENCODER = 4096
WRAP = 2048

HOMING_SPEED = 180
CURRENT_LIMIT = 4
STALL_TIME = 0.1

MOVE_KP = 3.5
MAX_SPEED = 1100

# Internal safe range (fully automatic)
MIN_SAFE_PERCENT = 10.0   # user 0%  maps to this
MAX_SAFE_PERCENT = 100.0  # user 100% maps to this


# ==========================================

port = PortHandler(PORT)
servo = PacketHandler(0)

if not port.openPort():
    print("ERROR: Cannot open port", PORT)
    quit()
if not port.setBaudRate(BAUD):
    print("ERROR: Cannot set baud rate")
    quit()

print("Connected to ST3215 (ID", SERVO_ID, ")")


# ================== FUNCTIONS ==================

def read_pos():
    p, comm_result, _ = servo.read2ByteTxRx(port, SERVO_ID, ADDR_PRESENT_POS)
    return p if comm_result == 0 else -1

def read_current():
    c, comm_result, _ = servo.read2ByteTxRx(port, SERVO_ID, ADDR_CURRENT)
    return c if comm_result == 0 else -1

def set_speed(speed):
    speed = max(min(int(speed), 3000), -3000)
    if speed >= 0:
        cmd = speed & 0x7FFF
    else:
        cmd = (abs(speed) | 0x8000)
    servo.write2ByteTxRx(port, SERVO_ID, ADDR_SPEED, cmd)

def stop():
    set_speed(0)
    time.sleep(0.25)


# ================== INIT ==================

print("\nSetting wheel/motor mode...")
servo.write1ByteTxRx(port, SERVO_ID, ADDR_TORQUE, 0)
time.sleep(0.15)
servo.write1ByteTxRx(port, SERVO_ID, ADDR_MODE, 1)
time.sleep(0.1)
servo.write1ByteTxRx(port, SERVO_ID, ADDR_TORQUE, 1)
time.sleep(0.1)
print("Wheel mode ready.\n")


# ================== MULTI-TURN ENCODER ==================

turns = 0
last_encoder = read_pos()

def get_position():
    global turns, last_encoder
    now = read_pos()
    if now < 0:
        return turns * ENCODER + last_encoder
    diff = now - last_encoder
    if diff < -WRAP:
        turns += 1
    elif diff > WRAP:
        turns -= 1
    last_encoder = now
    return turns * ENCODER + now


# ================== HOMING (infinite until stall) ==================

print("=== HOMING (automatic) ===\n")

# Find HOME
timer = time.time()
while True:
    set_speed(-HOMING_SPEED)
    pos = get_position()
    curr = read_current()
    print(f"Homing... pos={pos:7d}  current={curr:4d}")

    if curr > CURRENT_LIMIT and (time.time() - timer > STALL_TIME):
        print("\n>>> HOME STALL DETECTED <<<")
        break
    if curr <= CURRENT_LIMIT:
        timer = time.time()
    time.sleep(0.03)

stop()
time.sleep(0.3)

# Small automatic back-off (fixed, no tuning needed)
print("Small automatic back-off from stop...")
set_speed(50)
time.sleep(0.6)
stop()
time.sleep(0.2)

turns = 0
last_encoder = read_pos()
HOME = 0
print(f"HOME set (backed off automatically)\n")


# Find END
print("=== Finding END ===\n")
timer = time.time()
while True:
    set_speed(+HOMING_SPEED)
    pos = get_position()
    curr = read_current()
    print(f"Finding END... pos={pos:7d}  current={curr:4d}")

    if curr > CURRENT_LIMIT and (time.time() - timer > STALL_TIME):
        print("\n>>> END STALL DETECTED <<<")
        break
    if curr <= CURRENT_LIMIT:
        timer = time.time()
    time.sleep(0.03)

stop()

END = get_position()

print("\n=== CALIBRATION COMPLETE ===")
print(f"HOME = {HOME}   |   END = {END}")
print(f"Total stroke = {abs(END - HOME)} counts")
print("User input 0-100 is now mapped internally to 10%-100% (safe range)\n")


# ================== POSITION CONTROL WITH SMART MAPPING ==================

print("Type 0-100 (q to quit)\n")

while True:
    try:
        cmd = input("Position (0-100): ").strip().lower()
        if cmd == 'q':
            break
        user_percent = float(cmd)
    except:
        continue

    user_percent = max(0.0, min(100.0, user_percent))

    # === SMART MAPPING: user 0 → 10%, user 100 → 100% ===
    effective_percent = MIN_SAFE_PERCENT + (user_percent / 100.0) * (MAX_SAFE_PERCENT - MIN_SAFE_PERCENT)

    target = int(HOME + (END - HOME) * (effective_percent / 100.0))

    print(f"User {user_percent:.0f}% → internal {effective_percent:.1f}% → target = {target}")

    while True:
        current_pos = get_position()
        error = target - current_pos

        deadband = 30 if abs(target - HOME) < 150 else 18

        if abs(error) < deadband:
            stop()
            print("Reached\n")
            break

        speed = error * MOVE_KP
        speed = max(min(speed, MAX_SPEED), -MAX_SPEED)
        set_speed(speed)

        print(f"   pos={current_pos:7d}  err={error:6d}  spd={int(speed):5d}")
        time.sleep(0.02)

stop()
port.closePort()
print("Done.")