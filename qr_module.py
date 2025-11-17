from evdev import InputDevice, categorize, ecodes, list_devices
import json
import datetime
import select

from config import qrpath

# run this if needed
def find_gm65_device():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        if "USBKEY CHIP" in device.name.upper():
            print(f"✅ Found GM65 at {device.path} ({device.name})")
            return device.path
    raise RuntimeError("❌ GM65 not found")

def init_qr():
    global device, barcode
    try:
        # if not qrpath:
        qrpath = find_gm65_device()
        # Note: Adjust '/dev/input/event0' to the correct event device for the GM65 scanner.
        # You can list devices with: python3 -c "from evdev import list_devices; print(list_devices())"
        device = InputDevice(qrpath) #update event
        barcode = ""
        print('QR scanner initialized successfully.')
        return True
    except Exception as e:
        print('QR scanner initialization failed!')
        print('Exception message: ' + str(e))
        return False

def check_qr(timeout=1.0):
    global barcode
    try:
        r, _, _ = select.select([device], [], [], timeout)
        if not r:
            return None

        for event in device.read():
            if event.type == ecodes.EV_KEY:
                data = categorize(event)
                if data.keystate == 1:  # key down
                    key = data.keycode.replace('KEY_', '')

                    # 🔹 Chỉ nhận số & chữ cái
                    if key.isdigit():
                        barcode += key
                    elif len(key) == 1 and key.isalpha():
                        barcode += key.lower()
                    elif key == 'ENTER':
                        if barcode:
                            result = {
                                "event": "qr",
                                "code": 0,
                                "data": barcode,
                                "time": datetime.datetime.now().isoformat()
                            }
                            barcode = ""
                            return result
                    else:
                        # Bỏ qua các phím hệ thống như CAPSLOCK, SHIFT, ...
                        pass
        return None
    except Exception as e:
        print(f"Error checking QR: {e}")
        return None
