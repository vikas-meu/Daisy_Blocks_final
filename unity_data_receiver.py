#!/usr/bin/env python3
"""
VR to ST3215 Servo Controller
Receives JSON data from Unity via TCP and maps it to 20 servos with configurable 3-point mapping.
"""

import socket
import serial
import json
import time
import sys
from typing import Dict, List, Optional

# ============================================================
# ====================== CONFIGURATION =======================
# ============================================================

TCP_HOST = "0.0.0.0"
TCP_PORT = 8080

SERVO_PORT = "/dev/ttyACM0"
SERVO_BAUD = 1000000

# Servo movement parameters
SERVO_SPEED = 1500
SERVO_ACC = 50

# Smoothing and deadband (global)
SMOOTH_FACTOR = 0.75          # 0.0 = no smoothing, 1.0 = very smooth
DEADBAND = 3                  # minimum change in servo units before sending command

# Default servo position limits (ST3215: 0-4095)
SERVO_ABSOLUTE_MIN = 100
SERVO_ABSOLUTE_MAX = 4000

# ============================================================
# ==================== SERVO CONFIGURATION ===================
# ============================================================
# >>>>> EASY TO MODIFY LATER <<<<<
# Each servo has its own input range and servo range.
# Format: [input_min, input_mid, input_max]  ->  [servo_min, servo_mid, servo_max]

SERVO_CONFIG: Dict[int, dict] = {
    # === CUBE 0 POSITION (IDs 1-3) ===
    1: {"name": "cube_pos_x",   "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    2: {"name": "cube_pos_y",   "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    3: {"name": "cube_pos_z",   "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},

    # === CUBE 1 POSITION (IDs 4-6) ===
    4: {"name": "cube1_pos_x",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    5: {"name": "cube1_pos_y",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    6: {"name": "cube1_pos_z",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},

    # === CUBE 2 POSITION (IDs 7-9) ===
    7: {"name": "cube2_pos_x",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    8: {"name": "cube2_pos_y",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},
    9: {"name": "cube2_pos_z",  "input_range": [-6.0, 0.0, 6.0],   "servo_range": [500, 2048, 3500], "enabled": True},

    # === CUBE 0 ROTATION (IDs 10-12) ===
    10: {"name": "cube_rot_x",  "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    11: {"name": "cube_rot_y",  "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    12: {"name": "cube_rot_z",  "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},

    # === CUBE 1 ROTATION (IDs 13-15) ===
    13: {"name": "cube1_rot_x", "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    14: {"name": "cube1_rot_y", "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    15: {"name": "cube1_rot_z", "input_range": [-120.0, 0.0, 120.0], "servo_range": [1029, 2000, 3060], "enabled": True},

    # === CUBE 2 ROTATION (IDs 16-18) ===
    16: {"name": "cube2_rot_x", "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    17: {"name": "cube2_rot_y", "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},
    18: {"name": "cube2_rot_z", "input_range": [-90.0, 0.0, 90.0], "servo_range": [500, 2048, 3500], "enabled": True},

    # === TRIGGERS (IDs 19-20) ===
    19: {"name": "left_trigger",  "input_range": [0.0, 0.5, 1.0],   "servo_range": [1000, 1500, 2000], "enabled": True},  # Example: only partially enabled
    20: {"name": "right_trigger", "input_range": [0.0, 0.5, 1.0],   "servo_range": [2311, 2048, 3388], "enabled": True},
}

# ============================================================
# ==================== MAPPING FUNCTION ======================
# ============================================================

def map_three_point(value: float, in_min: float, in_mid: float, in_max: float,
                    out_min: float, out_mid: float, out_max: float) -> float:
    """
    Maps a value from a 3-point input range to a 3-point output range.
    """
    if value <= in_min:
        return out_min
    if value >= in_max:
        return out_max

    if value <= in_mid:
        if (in_mid - in_min) == 0:
            return out_min
        t = (value - in_min) / (in_mid - in_min)
        return out_min + t * (out_mid - out_min)
    else:
        if (in_max - in_mid) == 0:
            return out_mid
        t = (value - in_mid) / (in_max - in_mid)
        return out_mid + t * (out_max - out_mid)


def get_servo_position(servo_id: int, input_value: float) -> Optional[int]:
    if servo_id not in SERVO_CONFIG:
        return None

    cfg = SERVO_CONFIG[servo_id]
    if not cfg.get("enabled", True):
        return None

    in_min, in_mid, in_max = cfg["input_range"]
    out_min, out_mid, out_max = cfg["servo_range"]

    mapped = map_three_point(input_value, in_min, in_mid, in_max, out_min, out_mid, out_max)
    mapped = max(out_min, min(out_max, mapped))
    return int(mapped)


# ============================================================
# ==================== SERVO CONTROLLER ======================
# ============================================================

class ServoController:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=0)
        print(f"[Servo] Connected to {port} @ {baud} baud")

        self.smooth: Dict[int, float] = {}
        self.last_sent: Dict[int, int] = {}

        for sid in SERVO_CONFIG:
            mid = (SERVO_CONFIG[sid]["servo_range"][0] + SERVO_CONFIG[sid]["servo_range"][2]) // 2
            self.smooth[sid] = float(mid)
            self.last_sent[sid] = mid

    def _checksum(self, packet: List[int]) -> int:
        return (~sum(packet[2:])) & 0xFF

    def write_pos(self, sid: int, pos: int, speed: int = SERVO_SPEED, acc: int = SERVO_ACC):
        pos = max(SERVO_ABSOLUTE_MIN, min(SERVO_ABSOLUTE_MAX, int(pos)))

        packet = [
            0xFF, 0xFF, sid, 0x09, 0x03, 0x2A,
            pos & 0xFF, (pos >> 8) & 0xFF,
            0x00, 0x00,
            speed & 0xFF, (speed >> 8) & 0xFF,
            acc
        ]
        packet[3] = len(packet) - 3
        packet.append(self._checksum(packet))

        try:
            self.ser.write(bytes(packet))
        except Exception as e:
            print(f"[Servo] Write error on ID {sid}: {e}")

    def move_servo(self, sid: int, input_value: float):
        target = get_servo_position(sid, input_value)
        if target is None:
            return

        # Smoothing
        self.smooth[sid] = self.smooth[sid] * (1 - SMOOTH_FACTOR) + target * SMOOTH_FACTOR
        final = int(round(self.smooth[sid]))

        # Deadband
        if abs(final - self.last_sent[sid]) < DEADBAND:
            return

        self.last_sent[sid] = final
        self.write_pos(sid, final)

    def close(self):
        try:
            self.ser.close()
        except:
            pass


# ============================================================
# ==================== VR DATA RECEIVER ======================
# ============================================================

class VRReceiver:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.conn = None
        self.buffer = ""

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        print(f"[TCP] Waiting for Unity connection on {self.host}:{self.port}...")

        self.conn, addr = server.accept()
        print(f"[TCP] Unity connected from {addr}")

    def receive_data(self) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            data = self.conn.recv(8192)
            if not data:
                return None

            self.buffer += data.decode(errors="ignore")

            if "\n" in self.buffer:
                lines = self.buffer.split("\n")
                self.buffer = lines[-1]
                for line in lines[:-1]:
                    line = line.strip()
                    if line:
                        try:
                            return json.loads(line)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"[TCP] Receive error: {e}")
        return None

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass


# ============================================================
# ====================== MAIN LOOP ===========================
# ============================================================

def main():
    print("=" * 60)
    print("VR → ST3215 Servo Controller (20 Servos)")
    print("=" * 60)

    servo_ctrl = ServoController(SERVO_PORT, SERVO_BAUD)
    vr = VRReceiver(TCP_HOST, TCP_PORT)

    try:
        vr.start()
    except Exception as e:
        print(f"[ERROR] Failed to start TCP server: {e}")
        servo_ctrl.close()
        sys.exit(1)

    print("\n[INFO] System ready. Waiting for VR data...\n")

    # Clean mapping from JSON structure → Servo ID
    AXIS_MAP = {
        # Position
        ("cube", "position", "x"): 1,
        ("cube", "position", "y"): 2,
        ("cube", "position", "z"): 3,
        ("cube1", "position", "x"): 4,
        ("cube1", "position", "y"): 5,
        ("cube1", "position", "z"): 6,
        ("cube2", "position", "x"): 7,
        ("cube2", "position", "y"): 8,
        ("cube2", "position", "z"): 9,
        # Rotation
        ("cube", "rotation", "x"): 10,
        ("cube", "rotation", "y"): 11,
        ("cube", "rotation", "z"): 12,
        ("cube1", "rotation", "x"): 13,
        ("cube1", "rotation", "y"): 14,
        ("cube1", "rotation", "z"): 15,
        ("cube2", "rotation", "x"): 16,
        ("cube2", "rotation", "y"): 17,
        ("cube2", "rotation", "z"): 18,
        # Triggers
        ("trig1",): 19,
        ("trig2",): 20,
    }

    while True:
        packet = vr.receive_data()
        if packet is None:
            time.sleep(0.005)
            continue

        try:
            for key_tuple, servo_id in AXIS_MAP.items():
                try:
                    if len(key_tuple) == 3:
                        obj, sub, axis = key_tuple
                        value = packet[obj][sub][axis]
                    else:
                        value = packet[key_tuple[0]]

                    servo_ctrl.move_servo(servo_id, float(value))
                except (KeyError, TypeError):
                    continue  # Missing data for this axis - skip

        except Exception as e:
            print(f"[Main] Processing error: {e}")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down gracefully...")