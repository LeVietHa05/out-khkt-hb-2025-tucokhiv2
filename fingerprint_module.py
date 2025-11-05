import adafruit_fingerprint
import serial
import json
import datetime
import time

state_queue = None

def set_state_queue(queue):
    global state_queue
    state_queue = queue

def update_state(message):
    if state_queue:
        state_queue.put(message)

def init_fingerprint():
    global finger
    try:
        # Initialize UART connection
        uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        if finger.verify_password() != adafruit_fingerprint.OK:
            raise ValueError('Fingerprint sensor password is wrong!')

        print('Fingerprint sensor initialized successfully.')

        # Get template count
        if finger.count_templates() != adafruit_fingerprint.OK:
            raise RuntimeError('Failed to get template count')
        template_count = finger.template_count
        print(f'Currently stored fingers: {template_count}')
        return True
    except Exception as e:
        print('Fingerprint sensor initialization failed!')
        print('Exception message: ' + str(e))
        return False

def check_fingerprint():
    try:
        if finger.get_image() == adafruit_fingerprint.OK:
            print('Image taken')

            if finger.image_2_tz(1) == adafruit_fingerprint.OK:
                if finger.finger_search() == adafruit_fingerprint.OK:
                    print(f'Match found at position {finger.finger_id}')
                    timestamp = datetime.datetime.now().isoformat()
                    update_state({
                        "event": "finger",
                        "code": 0,  # good code
                        "data": finger.finger_id,
                        "time": timestamp
                    })
                else:
                    print('No match found')
                    timestamp = datetime.datetime.now().isoformat()
                    update_state({
                        "event": "finger",
                        "code": 1,  # error code
                        "data": "not register",
                        "time": timestamp
                    })
            else:
                print('Failed to convert image')
                update_state({
                        "event": "finger",
                        "code": 0,  # good code
                        "data": finger.finger_id,
                        "time": timestamp
                    })
        # No sleep here, as it's polled
    except Exception as e:
        timestamp = datetime.datetime.now().isoformat()
        update_state({
            "event": "finger",
            "code": 1,  # error code
            "data": "something gone wrong",
            "time": timestamp
        })
        print('Operation failed!')
        print('Exception message: ' + str(e))
    
    


def enroll_fingerprint():
    try:
        # Initialize UART connection
        uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        if finger.verify_password() != adafruit_fingerprint.OK:
            raise ValueError('Fingerprint sensor password is wrong!')

        print('Place finger on sensor...')
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        print('Image taken')

        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            raise RuntimeError('Failed to convert image')

        timestamp = datetime.datetime.now().isoformat()

        # Check if finger is already enrolled
        if finger.finger_search() == adafruit_fingerprint.OK:
            update_state({
                "event": "register finger",
                "code": 1,  # error code
                "data": "finger already register",
                "time": timestamp
            })
            print(f'Template already exists at position {finger.finger_id}')
            return None

        update_state({
            "event": "register finger",
            "code": 0,
            "data": "stage 1 done, remove finger",
            "time": timestamp
        })
        print('Remove finger...')
        time.sleep(2)

        update_state({
            "event": "register finger",
            "code": 0,
            "data": "stage 2 done, place same finger",
            "time": timestamp
        })
        print('Place same finger again...')
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        print('Image taken')

        if finger.image_2_tz(2) != adafruit_fingerprint.OK:
            raise RuntimeError('Failed to convert second image')

        if finger.create_model() != adafruit_fingerprint.OK:
            update_state({
                "event": "register finger",
                "code": 1,
                "data": "finger do not match",
                "time": timestamp
            })
            raise Exception('Fingers do not match')
        
        def find_empty_slot():
            """Tìm một vị trí trống (ID) để lưu vân tay mới."""
            for slot in range(1, finger.library_size + 1):  # library_size là số vị trí tối đa (127 hoặc 162)
                # Kiểm tra xem vị trí có trống không
                finger.read_templates()  # Đọc danh sách các template đã sử dụng
                if slot not in finger.templates:  # Nếu slot không nằm trong danh sách đã sử dụng
                    return slot
            return None  # Trả về None nếu không còn vị trí trống

        positionNumber = find_empty_slot()
        if finger.store_model(positionNumber) != adafruit_fingerprint.OK:  # Store at position 0, or find next available
            raise RuntimeError('Failed to store model')

        update_state({
            "event": "register finger",
            "code": 0,
            "data": "register done",
            "positionNumber": positionNumber,
            "time": timestamp
        })

        print(f'Fingerprint enrolled at position {positionNumber}')
        return positionNumber
    except Exception as e:
        timestamp = datetime.datetime.now().isoformat()
        update_state({
            "event": "register finger",
            "code": 1,
            "data": str(e),
            "time": timestamp
        })
        print(f'Error during enrollment: {e}')
        return None