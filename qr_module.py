from evdev import InputDevice, categorize, ecodes
import json
import datetime

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

def check_qr():
    global barcode
    try:
        event = device.read_one()
        if event and event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 1:  # Key down
                if data.keycode == 'KEY_ENTER':
                    if barcode:
                        timestamp = datetime.datetime.now().isoformat()
                        data = {
                            "event" : "qr",
                            "code" : 0,
                            "data": barcode,
                            "time": timestamp
                        }
                        barcode = ""
                        return data
                else:
                    key = data.keycode.replace('KEY_', '')
                    barcode += key.lower()
        return None
    except Exception as e:
        print('Error checking QR: ' + str(e))
        return None
