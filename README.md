

# Cài requirement.txt
``` bash 
pip install -r requirements.txt
```


# 1. Cài thư viện cho module fingerprint
# 🔹 Bước 1: Kích hoạt môi trường ảo (khuyến khích)

Việc này giúp bạn tránh xung đột thư viện giữa các project.

``` bash
python3 -m venv venv
source venv/bin/activate      # Linux / Raspberry Pi
# hoặc venv\Scripts\activate  # Windows
```

# 🔹 Bước 2: Cài thư viện PyFingerprint

Cài trực tiếp từ PyPI:

``` bash
pip install pyfingerprint
```
### Nếu Pi của bạn báo lỗi biên dịch hoặc không có gói prebuilt, thì có thể thử:
``` bash
pip install pyserial
git clone https://github.com/bastianraschke/pyfingerprint.git
cd pyfingerprint/src
sudo python3 setup.py install
```
### ✅ Giải thích:
- pyserial: cần cho giao tiếp UART.
- pyfingerprint: là thư viện chính để làm việc với cảm biến vân tay dòng R30x, GT-511, ZFM-20, v.v.
# 2. Kiểm tra cài đặt

Sau khi cài xong, thử:

python3 -c "from pyfingerprint import PyFingerprint; print('✅ PyFingerprint installed successfully!')"


Nếu thấy dòng xác nhận → OK.