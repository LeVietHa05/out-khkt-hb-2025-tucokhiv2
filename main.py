import time
import queue
import requests
from fingerprint_module import init_fingerprint, check_fingerprint, enroll_fingerprint, set_state_queue as set_fp_state
from qr_module import init_qr, check_qr, set_state_queue as set_qr_state

serverUrl = 'http://172.16.30.142:3000'

state_queue = queue.Queue()

set_fp_state(state_queue)
set_qr_state(state_queue)

# Initialize modules
fp_initialized = init_fingerprint()
qr_initialized = init_qr()

def main_loop():
    last_command_check = 0
    while True:
        current_time = time.time()

        # Check fingerprint if initialized
        if fp_initialized:
            check_fingerprint()

        # Check QR if initialized
        if qr_initialized:
            check_qr()

        # Post state if available
        try:
            state = state_queue.get_nowait()
            requests.post(serverUrl + '/api/state', json=state)
        except queue.Empty:
            pass
        except Exception as e:
            print(f'Error posting state: {e}')

        # Fetch command every 1 second
        if current_time - last_command_check >= 1:
            try:
                response = requests.get(serverUrl + '/api/command', timeout=3)
                command = response.json()

                if command['command'] == 'enroll_fingerprint':
                    print("🆕 Enrolling new fingerprint...")
                    result = enroll_fingerprint()
                    requests.post(serverUrl + '/api/erroll_result', json=result)

                last_command_check = current_time
            except Exception as e:
                print(f"⚠️ Lỗi khi fetch command: {e}")
                # On error, wait 10 seconds before retrying
                last_command_check = current_time + 9  # +9 to make total 10 seconds

        # Small sleep to prevent busy waiting
        time.sleep(0.1)

if __name__ == '__main__':
    main_loop()
