from evdev import InputDevice, categorize, ecodes
import json
import datetime

state_queue = None

def set_state_queue(queue):
    global state_queue
    state_queue = queue

def update_state(message):
    if state_queue:
        state_queue.put(message)

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
                        
                        update_state({
                            "event" : "qr",
                            "code" : 0,
                            "data": barcode,
                            "time": timestamp
                        })
                        barcode = ""
                else:
                    key = data.keycode.replace('KEY_', '')
                    barcode += key.lower()
