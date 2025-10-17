import adafruit_fingerprint
import serial

def reset_fingerprint_sensor():
    try:
        # Initialize UART connection
        uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        if finger.verify_password() != adafruit_fingerprint.OK:
            raise ValueError('Fingerprint sensor password is wrong!')

        print('Fingerprint sensor initialized successfully.')

        # Empty the library (delete all stored templates)
        if finger.empty_library() != adafruit_fingerprint.OK:
            raise RuntimeError('Failed to empty the fingerprint library')

        print('All fingerprints have been reset. Library is now empty.')

    except Exception as e:
        print('Reset operation failed!')
        print('Exception message: ' + str(e))

if __name__ == '__main__':
    reset_fingerprint_sensor()
