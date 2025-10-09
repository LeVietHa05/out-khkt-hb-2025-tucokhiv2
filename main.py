import threading
import time
from ai_module import detect_tools
from fingerprint_module import verify_fingerprint
from qr_module import read_qr

def ai_loop():
    detect_tools()

def fingerprint_loop():
    verify_fingerprint()

def qr_loop():
    read_qr()

if __name__ == '__main__':
    t1 = threading.Thread(target=ai_loop)
    t2 = threading.Thread(target=fingerprint_loop)
    t3 = threading.Thread(target=qr_loop)

    t1.start()
    t2.start()
    t3.start()

    # Keep main thread alive
    t1.join()
    t2.join()
    t3.join()
