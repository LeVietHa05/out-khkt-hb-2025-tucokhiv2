import queue
import threading
import time
from fingerprint_module import enroll_fingerprint, verify_fingerprint, set_state_queue

# Set up state queue for testing
state_queue = queue.Queue()
set_state_queue(state_queue)

def print_states():
    """Print all state updates from the queue."""
    while True:
        try:
            state = state_queue.get(timeout=0.1)
            print(f"State update: {state}")
        except queue.Empty:
            break

def test_enroll():
    """Test the enroll_fingerprint function."""
    print("Starting fingerprint enrollment test...")
    try:
        position = enroll_fingerprint()
        if position is not None:
            print(f"Fingerprint enrolled successfully at position {position}")
        else:
            print("Enrollment failed.")
    except Exception as e:
        print(f"Error during enrollment: {e}")
    print_states()

def test_verify():
    """Test the verify_fingerprint function for a limited time."""
    print("Starting fingerprint verification test (running for 30 seconds)...")
    try:
        # Run verify in a thread
        verify_thread = threading.Thread(target=verify_fingerprint)
        verify_thread.daemon = True  # Allow main thread to exit
        verify_thread.start()

        # Let it run for 30 seconds
        time.sleep(30)
        print("Verification test completed.")
    except Exception as e:
        print(f"Error during verification: {e}")
    print_states()

if __name__ == '__main__':
    print("Fingerprint Module Test")
    print("1. Test Enroll")
    print("2. Test Verify")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        test_enroll()
    elif choice == '2':
        test_verify()
    else:
        print("Invalid choice.")
