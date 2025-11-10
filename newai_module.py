import io
import time
import subprocess
import requests

SERVER_URL = "http://172.16.30.124:3000/api/image"

def send_image():
    """
    Chụp ảnh bằng rpicam-still và gửi lên server qua HTTP POST.
    """
    try:
        # Dùng rpicam-still để chụp ảnh tạm
        temp_path = "/tmp/capture.jpg"
        subprocess.run(
            ["rpicam-still", "-n", "-t", "500", "-o", temp_path, "--width", "1280", "--height", "720"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Đọc ảnh và gửi lên server
        with open(temp_path, "rb") as f:
            files = {"file": ("capture.jpg", f, "image/jpeg")}
            response = requests.post(SERVER_URL, files=files, timeout=10)

        if response.status_code == 200:
            print("✅ Ảnh đã gửi thành công!")
        else:
            print(f"⚠️ Server trả về lỗi: {response.status_code} - {response.text}")

    except subprocess.CalledProcessError:
        print("❌ Lỗi khi chụp ảnh (camera hoặc lệnh rpicam-still bị lỗi)")
    except Exception as e:
        print(f"❌ Lỗi khi gửi ảnh: {e}")
