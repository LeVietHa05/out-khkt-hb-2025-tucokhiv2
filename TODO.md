# TODO List for QR Module Modification

- [x] Modify qr_module.py:
  - Remove state_queue, set_state_queue, and update_state functions.
  - Add import requests.
  - Add serverUrl = 'http://172.16.30.142:3000'.
  - In check_qr function, replace update_state call with requests.post(serverUrl + '/api/qr', json={...}).

- [x] Update qr_module.py:
  - Remove import requests and serverUrl.
  - Modify check_qr to return barcode data when scan successful, else return None.

- [x] Update main.py:
  - In main_loop, call check_qr and if it returns data, POST to '/api/qr'.
