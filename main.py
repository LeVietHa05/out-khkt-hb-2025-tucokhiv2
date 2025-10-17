import threading
import time
import queue
import requests
#from ai_module import detect_tools, set_state_queue as set_ai_state
from fingerprint_module import verify_fingerprint, enroll_fingerprint,  set_state_queue as set_fp_state
from qr_module import read_qr, set_state_queue as set_qr_state

serverUrl = 'http://172.16.30.167:3000'

state_queue = queue.Queue()
message_queue = queue.Queue()  # For results

#set_ai_state(state_queue)
set_fp_state(state_queue)
set_qr_state(state_queue)

# def ai_loop():
#    detect_tools()

def fingerprint_loop():
    verify_fingerprint()

def qr_loop():
    read_qr()


#update current machine state to server
def post_state():
    while True:
        try:
            state = state_queue.get(timeout=1)
            requests.post(serverUrl + '/api/state', json=state)
        except queue.Empty:
            pass
        except Exception as e:
            print(f'Error posting state: {e}')

def fetch_command():
    while True:
        try:
            # Gọi API để kiểm tra xem server có yêu cầu gì không
            response = requests.get(serverUrl + '/api/command', timeout=3)
            command = response.json()

            # Nếu server yêu cầu quét vân tay
            if (command['command'] == 'enroll_fingerprint'):
                print("🆕 Enrolling new fingerprint...")
                result = enroll_fingerprint()

                # Gửi kết quả xác thực ngược lại server
                requests.post(serverUrl + '/api/erroll_result', json=result)

            time.sleep(1)  # 1 giây kiểm tra 1 lần

        except Exception as e:
            print(f"⚠️ Lỗi khi fetch command: {e}")
            time.sleep(10)


if __name__ == '__main__':
    # t1 = threading.Thread(target=ai_loop)
    t2 = threading.Thread(target=fingerprint_loop)
    # t3 = threading.Thread(target=qr_loop)
    t4 = threading.Thread(target=post_state)
    t5 = threading.Thread(target=fetch_command)

    # t1.start()
    t2.start()
    # t3.start()
    t4.start()
    t5.start()

    # Keep main thread alive
    # t1.join()
    t2.join()
    # t3.join()
    t4.join()
    t5.join()
