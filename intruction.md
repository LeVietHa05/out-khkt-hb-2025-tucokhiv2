# 🔧 Raspberry Pi 4 Multi-Module System for Tool Cabinet

This document describes a small-scale Raspberry Pi 4 project used to **detect tools**, **verify user identity via fingerprint**, and **read QR codes** inside a tool cabinet.  
The system runs all three modules simultaneously and exchanges data through topics (e.g., websocket).

---

## 🧠 Overview

### System Description

A single-tier tool cabinet with a top-mounted camera (≈70 cm above the tools).  
The Raspberry Pi 4 performs three tasks:

1. **Tool Detection (AI Module)** – captures an image every 2 seconds and identifies which tools are present and where they are located.
2. **Fingerprint Module** – verifies the identity of the user accessing the cabinet.
3. **QR Code Module** – scans barcodes or QR codes placed on tools or trays, then logs and publishes the results.

Each module runs in its own thread or process to allow parallel execution.

---

## ⚙️ Hardware Setup

| Component                         | Description                           | Connection  |
| --------------------------------- | ------------------------------------- | ----------- |
| **Raspberry Pi 4**                | Main controller                       | —           |
| **Camera (CSI)**                  | Captures tool images for AI detection | CSI Port    |
| **Fingerprint Sensor (use R307)** | Reads and verifies fingerprint data   | UART or USB |
| **QR Code Scanner (use GM65)**    | Scans QR/barcode from tools or trays  | USB or UART |
| **Power Supply (≥3A)**            | Stable power for all devices          | 5V/3A       |

---

## 🧩 Module 1 – Tool Detection (AI Module)

### Description

- Captures an image every 2 seconds.
- Uses a lightweight AI model (e.g., YOLOv5n or MobileNet SSD via TensorFlow Lite).
- Detects which tools are present and returns their bounding box positions.
- Sends detection results to topic: `tools/detection_result`.

### Example Output

```json
{
  "timestamp": "2025-10-08T10:30:00",
  "tools": [
    { "name": "wrench", "x": 120, "y": 340 },
    { "name": "screwdriver", "x": 250, "y": 210 }
  ]
}
```

### Steps to Implement

Focus on module 2 and 3 first. skip this module for later

1. Install camera driver and OpenCV:
2. sudo apt install python3-opencv
3. Load TensorFlow Lite or YOLOv5n model.
4. Create a Python loop that:
5. Captures image from CSI camera.
6. Runs inference every 2 seconds.
7. Publishes results to tools/detection_result via websocket.
8. Optimize model with quantization if CPU usage is high.

## 🧬 Module 2 – Fingerprint Verification Module

### Description

Reads and verifies fingerprints using a fingerprint sensor (UART or USB).
When a valid fingerprint is detected, the module publishes an event to topic: auth/fingerprint_result.

### Example Output

```json
{
  "timestamp": "2025-10-08T10:33:22",
  "user_id": "user_01",
  "verified": true
}
```

### Steps to Implement

1. Connect the fingerprint sensor to the Pi via UART or USB.
2. Install fingerprint library:
3. pip install pyfingerprint
4. Write Python code to:
5. Continuously read fingerprint data.
6. Compare fingerprint with stored templates.
7. Publish result (verified true/false) via websocket.
8. Optionally log fingerprint verification attempts to a local database
9. write the module and export it for the main threading

## 📦 Module 3 – QR Code Scanner Module

### Description

This module uses the **GM65 QR/Barcode Scanner** to read tool or tray labels inside the tool cabinet.  
When a code is detected, the scanner sends the data via **UART (serial)** to the Raspberry Pi 4.

The data will then be formatted into JSON and published to the websockets topic:

### Example Output

```json
{
  "timestamp": "2025-10-08T10:35:04",
  "id": "123124124"
}
```

### Steps to Implement

1. Connect a barcode/QR code reader via USB-HID mode.
2. run this

```code
sudo apt install python3-evdev
```

3. try this code, or create new code to read qr from usb hid mode

```pytthon
from evdev import InputDevice, categorize, ecodes

device = InputDevice('/dev/input/event0')  # hoặc event1, tuỳ vào thiết bị

barcode = ""

for event in device.read_loop():
    if event.type == ecodes.EV_KEY:
        data = categorize(event)
        if data.keystate == 1:  # Key down
            if data.keycode == 'KEY_ENTER':
                print("Scanned:", barcode)
                barcode = ""
            else:
                key = data.keycode.replace('KEY_', '')
                barcode += key.lower()

```
4. write the module and export it for the main threading

## 🧵 Running All Modules Together
run all thread, also create a new websocket server here
### Example Python Threading Setup

```python
import threading
import time
from ai_module import detect_tools
from fingerprint_module import verify_fingerprint
from qr_module import read_qr

def ai_loop():
    while True:
        detect_tools()
        time.sleep(2)

def fingerprint_loop():
    verify_fingerprint()

def qr_loop():
    read_qr()

t1 = threading.Thread(target=ai_loop)
t2 = threading.Thread(target=fingerprint_loop)
t3 = threading.Thread(target=qr_loop)

t1.start()
t2.start()
t3.start()
```

### Notes

1. Each module runs independently on its own CPU thread.
2. Use websocket or sockets to communicate between modules.
3. Store all logs with timestamps for traceability.
