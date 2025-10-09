from pyfingerprint import PyFingerprint
import json
import datetime
import time

def verify_fingerprint():
    # Initialize fingerprint sensor (using UART, adjust port as needed, e.g., '/dev/ttyAMA0' for Raspberry Pi UART)
    f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

    if not f.verifyPassword():
        raise ValueError('Fingerprint sensor password incorrect')

    ## Gets info about how many fingerprint are currently stored
    print('Currently stored fingers: {}/{}'.format(f.getTemplateCount(), f.getStorageCapacity()))

    # Assuming templates are stored; map position to user_id (update as needed)
    user_map = {0: 'user_01', 1: 'user_02'}  # Example mapping

    while True:
        print('Waiting for finger...')
        while not f.readImage():
            time.sleep(0.1)  # Small delay to avoid busy waiting

        f.convertImage(0x01)
        result = f.searchTemplate()

        if result[0] == -1:
            print('No match found')
            verified = False
            user_id = None
        else:
            print(f'Match found at position {result[0]}')
            verified = True
            user_id = user_map.get(result[0], f'template_{result[0]}')

        timestamp = datetime.datetime.now().isoformat()
        result_json = {
            "timestamp": timestamp,
            "user_id": user_id,
            "verified": verified
        }
        print(json.dumps(result_json))  # Publish to websocket topic later

        time.sleep(1)  # Delay before next scan

def enroll_fingerprint(position):
    # Initialize fingerprint sensor
    f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

    if not f.verifyPassword():
        raise ValueError('Fingerprint sensor password incorrect')

    print('Place finger on sensor...')
    while not f.readImage():
        time.sleep(0.1)

    f.convertImage(0x01)

    print('Remove finger...')
    time.sleep(2)

    print('Place same finger again...')
    while not f.readImage():
        time.sleep(0.1)

    f.convertImage(0x02)

    if f.compareCharacteristics() == 0:
        raise ValueError('Fingers do not match')

    f.createTemplate()
    positionNumber = f.storeTemplate(position)
    print(f'Fingerprint enrolled at position {positionNumber}')
    return positionNumber
