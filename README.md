```
🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼
                         ✨ DAISY BLOCKS FINAL ✨
      VR-Controlled Robotic Cube Manipulation with ST3215 Servos
🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼
```

---

## 🌸 Overview

**Daisy Blocks** is an innovative robotics project that bridges the gap between virtual reality and physical robotic control. This system receives real-time data from Unity VR applications and orchestrates 20 ST3215 servo motors to manipulate three independent robotic cubes with precision and grace.

Like petals on a daisy blooming in unison, each servo works together to create seamless, coordinated movements that bring digital dreams into tangible reality.

---

## 🌼 Features & Capabilities

### 🎮 Multi-Cube Control Architecture
- **3 Independent Robotic Cubes** - Each cube has complete 6-DOF control (position + rotation)
- **20 Servo Motors** - Precision-controlled via TCP communication from VR environment
- **Real-time Data Streaming** - Smooth, responsive movements synchronized with VR input

### 📊 Servo Configuration
```
🌷 CUBE 0 (Petals 1-3):     X, Y, Z Position      [IDs 1-3]
🌷 CUBE 0 (Petals 10-12):   X, Y, Z Rotation      [IDs 10-12]

🌻 CUBE 1 (Petals 4-6):     X, Y, Z Position      [IDs 4-6]
🌻 CUBE 1 (Petals 13-15):   X, Y, Z Rotation      [IDs 13-15]

🌹 CUBE 2 (Petals 7-9):     X, Y, Z Position      [IDs 7-9]
🌹 CUBE 2 (Petals 16-18):   X, Y, Z Rotation      [IDs 16-18]

🎯 Triggers (Petals 19-20): Left & Right Control  [IDs 19-20]
```

### ⚙️ Advanced Features

#### 🌟 Smart Position Mapping (Linear Actuator)
- **Automatic Calibration** - Self-discovers HOME and END positions without tuning
- **Safe Range Mapping** - User input 0-100% automatically maps to 10%-100% stroke (avoiding hard stops)
- **Stall Detection** - Uses current sensing to detect physical limits precisely
- **Multi-turn Encoder Support** - Tracks complete rotation range with 4096-count resolution

#### 🎯 Intelligent Servo Control
- **3-Point Mapping** - Flexible input-to-servo mapping for non-linear responses
- **Smoothing Algorithm** - Eliminates jitter with configurable smoothing factor (0.0-1.0)
- **Deadband Control** - Prevents unnecessary servo updates (configurable threshold)
- **Speed & Acceleration Control** - Smooth, predictable motion profiles

#### 🔌 VR Integration
- **TCP Server** - Listens on port 8080 for JSON data from Unity
- **JSON Protocol** - Clean, hierarchical data structure for cube positions and rotations
- **Error Tolerance** - Gracefully handles malformed or missing data
- **Real-time Synchronization** - Sub-5ms update loop for responsive VR interaction

---

## 📂 Project Structure

```
Daisy_Blocks_final/
│
├── 🌼 unity_data_receiver.py
│   └── Main TCP server receiving VR data from Unity
│       Coordinates all 20 servos with smooth, synchronized control
│
├── 🌻 linear_actuator_servo.py
│   └── Standalone controller for ST3215 linear actuator
│       Automatic calibration with smart mapping
│
├── 🌷 sm85cl_servo.py
│   └── Configuration and control utilities for SM85CL servos
│
└── 📜 LICENSE
    └── MIT License - Free to use and modify
```

---

## 🚀 Getting Started

### Prerequisites
```bash
# Install required Python libraries
pip install pyserial

# Download and build ScServo SDK
# Available at: https://github.com/SCServo/SCServo_Library_Python
```

### Hardware Setup
- **Controller Board**: ST3215 servo motors (× 20)
- **Serial Connection**: USB-to-serial adapter at `/dev/ttyACM0` (Linux) or `COM3` (Windows)
- **Network Interface**: TCP/IP connection for VR data (port 8080)
- **Power Supply**: 12V dedicated servo power supply

### Configuration

#### 🔧 Servo Configuration (`unity_data_receiver.py`)
```python
SERVO_CONFIG = {
    1: {
        "name": "cube_pos_x",
        "input_range": [-6.0, 0.0, 6.0],      # VR input range
        "servo_range": [500, 2048, 3500],     # Physical servo range
        "enabled": True
    },
    # ... more servos
}
```

#### 🎛️ Tuning Parameters
```python
SMOOTH_FACTOR = 0.75    # Increase for smoother, delayed response
DEADBAND = 3            # Servo units - higher = fewer updates
SERVO_SPEED = 1500      # Motor speed (0-3000)
SERVO_ACC = 50          # Acceleration smoothness
```

---

## 🎮 Running the System

### Method 1: Full VR Integration
```bash
python3 unity_data_receiver.py

# Output:
# ============================================================
# VR → ST3215 Servo Controller (20 Servos)
# ============================================================
# [Servo] Connected to /dev/ttyACM0 @ 1000000 baud
# [TCP] Waiting for Unity connection on 0.0.0.0:8080...
# [TCP] Unity connected from 127.0.0.1:12345
# [INFO] System ready. Waiting for VR data...
```

### Method 2: Direct Linear Actuator Control
```bash
python3 linear_actuator_servo.py

# Automatic sequence:
# 1. Finds HOME position (backward stall detection)
# 2. Auto back-off 10% from hard stop
# 3. Finds END position (forward stall detection)
# 4. Interactive 0-100% position control
```

---

## 📡 VR Data Format

Send JSON data to `localhost:8080` in this format:

```json
{
  "cube": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
  },
  "cube1": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
  },
  "cube2": {
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
  },
  "trig1": 0.5,
  "trig2": 0.5
}
```

Each line is processed independently - missing fields are safely ignored.

---

## 🛠️ Key Technologies & Techniques

| 🌼 Component | 🌻 Technology | 🌷 Purpose |
|---|---|---|
| **Motor Control** | ST3215 Protocol | Precise 16-bit position + speed control |
| **Serial Comm** | PySerial @ 1Mbps | Direct motor commanding |
| **VR Integration** | TCP Sockets | Real-time Unity ↔ Robot data flow |
| **Motion Control** | 3-point Mapping | Flexible input-output transformations |
| **Smoothing** | Exponential Moving Average | Natural, flowing motion |
| **Sensing** | Stall Current Detection | Automatic limit detection |
| **Encoding** | Multi-turn Encoder | Full rotation tracking (4096 counts) |

---

## 🌟 Advanced Features Explained

### 🎯 Smart Mapping Algorithm
```
User Input:        0%     25%    50%    75%    100%
                   |      |      |      |      |
Internal Mapping: 10%    32.5% 55%   77.5%  100%  ← Safe range (avoids hard stops)
                   |      |      |      |      |
Servo Position:   HOME  [---] [---] [---]  END
```

**Why?** Protects actuators from hitting hard physical stops at extreme positions.

### 🔄 3-Point Mapping
Supports non-linear response curves - useful when servo torque needs to vary across range:
- Input midpoint may not correspond to servo midpoint
- Enables smooth, realistic motion profiles
- Individually configurable per servo

### 🎨 Smoothing & Deadband
- **Deadband**: Prevents servo oscillation from minor noise
- **Smoothing**: Reduces jerky movements from network latency

---

## 🐛 Troubleshooting

| Problem | 🌼 Solution |
|---------|-----------|
| **Servo doesn't respond** | Check serial port (`/dev/ttyACM0`), verify baud rate (1000000) |
| **Unity can't connect** | Firewall settings, check TCP port 8080 is open |
| **Jerky movements** | Increase `SMOOTH_FACTOR`, check network latency |
| **Actuator hits hard stop** | Verify `MIN_SAFE_PERCENT` and `MAX_SAFE_PERCENT` values |
| **Current spike warnings** | Check `STALL_TIME` duration and `CURRENT_LIMIT` threshold |

---

## 📊 Performance Specifications

```
🌸 Communication Latency:     < 5ms per servo update
🌸 Serial Baud Rate:          1,000,000 bps
🌸 VR Update Rate:            UDP/TCP stream dependent
🌸 Servo Position Resolution: 4096 counts/revolution
🌸 Maximum Servos Supported:  20+ (expandable)
🌸 Motor Control Precision:   ±1 count (~0.09°)
🌸 Current Sensing Range:     0-5A (with 100mA resolution)
```

---

## 🎓 API Reference

### ServoController
```python
servo = ServoController("/dev/ttyACM0", 1000000)

# Move servo to position (with input value mapping)
servo.move_servo(servo_id=1, input_value=2.5)

# Direct position command
servo.write_pos(servo_id=1, pos=2048, speed=1500, acc=50)

# Cleanup
servo.close()
```

### VRReceiver
```python
vr = VRReceiver("0.0.0.0", 8080)
vr.start()  # Wait for connection

packet = vr.receive_data()  # Get next JSON packet
# Returns dict or None

vr.close()
```

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for personal and commercial projects.

---

## 🌼 Contributing & Support

Have improvements? Found a bug? Want to add features?

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 🎨 Project Vision

Daisy Blocks represents the intersection of digital and physical worlds - a demonstration of how VR can seamlessly control precision robotics. Like a daisy's petals working in harmony, each servo contributes to a unified, graceful movement system.

This project showcases:
- ✨ Real-time VR-to-robot communication
- ✨ Intelligent motion control algorithms
- ✨ Hardware abstraction for easy servo configuration
- ✨ Production-ready error handling and smoothing

---

## 📞 Contact & Credits

**Project**: Daisy Blocks Final  
**Author**: vikas-meu  
**Repository**: [github.com/vikas-meu/Daisy_Blocks_final](https://github.com/vikas-meu/Daisy_Blocks_final)

```
🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼
                    Built with ❤️ and plenty of 🌸 blooms
🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼 🌼
```

---

### 🌸 Thank You for Visiting! Enjoy the Blooms! 🌸
