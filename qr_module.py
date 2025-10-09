from evdev import InputDevice, categorize, ecodes
import json
import datetime

def read_qr():
    # Note: Adjust '/dev/input/event0' to the correct event device for the GM65 scanner.
    # You can list devices with: python3 -c "from evdev import list_devices; print(list_devices())"
    device = InputDevice('/dev/input/event0')
    barcode = ""
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            data = categorize(event)
            if data.keystate == 1:  # Key down
                if data.keycode == 'KEY_ENTER':
                    if barcode:
                        timestamp = datetime.datetime.now().isoformat()
                        result = {
                            "timestamp": timestamp,
                            "id": barcode
                        }
                        print(json.dumps(result))  # Publish to websocket topic later
                        barcode = ""
                else:
                    key = data.keycode.replace('KEY_', '')
                    barcode += key.lower()
