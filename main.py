import time
import queue
import requests
from fingerprint_module import init_fingerprint, check_fingerprint, enroll_fingerprint, set_state_queue as set_fp_state
from qr_module import init_qr, check_qr
from newai_module import send_image

serverUrl = 'http://172.16.30.124:3000'

state_queue = queue.Queue()

set_fp_state(state_queue)
# Initialize modules
fp_initialized = init_fingerprint()
qr_initialized = init_qr()

def main_loop():
    last_command_check = 0
    last_image_time = 0
    send_interval = 600  # mặc định 10 phút
    send_until = 0
    while True:
        current_time = time.time()

        # Check fingerprint if initialized
        if fp_initialized:
            check_fingerprint()

        # Check QR if initialized
        if qr_initialized:
            qr_data = check_qr()
            if qr_data is not None:
                try:
                    print(qr_data)
                    res= requests.post(serverUrl + '/api/qr', json=qr_data)
                    print(res)
                except Exception as e:
                    print(f'Error posting QR data: {e}')

        # Post state if available
        try:
            state = state_queue.get_nowait()
            requests.post(serverUrl + '/api/state', json=state)
            if state.event == "register finger"  and state.code == 0:
                time.sleep(1)
            
                # ✅ Nếu là sự kiện vân tay
            if state.event == "finger":
                current_time = time.time()
                if state.code == 0:
                    print("✅ Fingerprint matched! Start sending images every 5s for 1 minute.")
                    send_interval = 5
                    send_until = current_time + 60
                else:
                    print("❌ Fingerprint mismatch. Only one image per 10 minutes.")
                    send_interval = 600
                    send_until = current_time + 1  # chỉ gửi 1 lần
                    
        except queue.Empty:
            pass
        except Exception as e:
            print(f'Error posting state: {e}')

        # Fetch command every 2 second
        if current_time - last_command_check >= 2:
            try:
                response = requests.get(serverUrl + '/api/command', timeout=3)
                command = response.json()

                if command['command'] == 'enroll_fingerprint':
                    print("🆕 Enrolling new fingerprint...")
                    result = enroll_fingerprint()

                last_command_check = current_time
            except Exception as e:
                print(f"⚠️ Lỗi khi fetch command: {e}")
                # On error, wait 10 seconds before retrying
                last_command_check = current_time + 9  # +9 to make total 10 seconds

        # Gửi ảnh theo chu kỳ
        current_time = time.time()
        if current_time - last_image_time >= send_interval:
            if current_time <= send_until or send_interval >= 600:
                try:
                    # ⚙️ Gọi hàm gửi ảnh (bạn tự định nghĩa, ví dụ send_image())
                    print("📸 Sending image to server...")
                    # send_image()
                    last_image_time = current_time
                except Exception as e:
                    print(f"Error sending image: {e}")
                    
        # Small sleep to prevent busy waiting
        time.sleep(1.0)

if __name__ == '__main__':
    main_loop()
