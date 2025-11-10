from evdev import InputDevice, categorize, ecodes
import json
import datetime
import select

def init_qr():
    global device, barcode
    try:
        # Note: Adjust '/dev/input/event0' to the correct event device for the GM65 scanner.
        # You can list devices with: python3 -c "from evdev import list_devices; print(list_devices())"
        device = InputDevice('/dev/input/event10') #update event
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
