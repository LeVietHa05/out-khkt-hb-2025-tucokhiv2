from pyfingerprint import PyFingerprint
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

def verify_fingerprint():
   ## Tries to initialize the sensor
    try:
        f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    ## Gets info about how many fingerprint are currently stored
    print('Currently stored fingers: {}/{}'.format(f.getTemplateCount(), f.getStorageCapacity()))

    #TODO: update usermap or use server userid (just send finger position)
    # Assuming templates are stored; map position to user_id (update as needed)
    user_map = {0: 'user_01', 1: 'user_02'}  # Example mapping
    try:
        while True:
            print('Waiting for finger...')
            while not f.readImage():
                time.sleep(0.1)  # Small delay to avoid busy waiting
                pass
            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)
            result = f.searchTemplate()
            timestamp = datetime.datetime.now().isoformat()

            # result[0] is position, result[1] is accuracyscroe
            if result[0] == -1:
                update_state({
                    "event" : "finger",
                    "code" : 1, #error code 
                    "data": "not register",
                    "time": timestamp
                })
                print('No match found for this fingerprint')
                verified = False
                user_id = None
            else:
                print(f'Match found at position {result[0]}')
                verified = True
                # load the found template to charbuffer 1
                f.loadTemplate(result[0], 0x01)
                # in case no user-id found, use default template of fingerprint
                ## Downloads the characteristics of template loaded in charbuffer 1
                user_id = user_map.get(result[0], str(f.downloadCharacteristics(0x01)).encode('utf-8'))

            # update to queue
            update_state({
                "event" : "finger",
                "code" : 0, #good code
                "data": user_id,
                "time": timestamp
            })

            time.sleep(1)  # Delay before next scan
    except Exception as e:
        update_state({
            "event" : "finger",
            "code" : 1, #error code 
            "data": "something gone wrong",
            "time": timestamp
        })
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
    
    


def enroll_fingerprint():
    try:
        # Initialize fingerprint sensor
        f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise Exception('Fingerprint sensor password incorrect')

        print('Place finger on sensor...')
        while not f.readImage():
            pass

        f.convertImage(0x01)
        timestamp = datetime.datetime.now().isoformat()

        ## Checks if finger is already enrolled
        result = f.searchTemplate()
        positionNumber = result[0]

        if ( positionNumber >= 0 ):
            update_state({
                "event" : "register finger",
                "code" : 1, #error code 
                "data": "finger already register",
                "time": timestamp
            })
            print('Template already exists at position #' + str(positionNumber))
            return None

        update_state({
            "event" : "register finger",
            "code" : 0,
            "data": "stage 1 done, remove finger",
            "time": timestamp
        })
        print('Remove finger...')
        time.sleep(2)

        update_state({
            "event" : "register finger",
            "code" : 0, 
            "data": "stage 2 done, place same finger",
            "time": timestamp
        })
        print('Place same finger again...')
        while not f.readImage():
            pass

        f.convertImage(0x02)

        if f.compareCharacteristics() == 0:
            update_state({
                "event" : "register finger",
                "code" : 1, 
                "data": "finger do not match",
                "time": timestamp
            })
            raise Exception('Fingers do not match')

        f.createTemplate()
        positionNumber = f.storeTemplate()
        update_state({
            "event" : "register finger",
            "code" : 0, 
            "data": "register done",
            "positionNumber" : positionNumber,
            "time": timestamp
        })
        
        print(f'Fingerprint enrolled at position {positionNumber}')
        return positionNumber
    except Exception as e:
        update_state(f'Error during enrollment: {e}')
        print(f'Error during enrollment: {e}')
        return None
