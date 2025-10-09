import cv2
import time
import json
import datetime
import numpy as np
from tflite_runtime.interpreter import Interpreter

# Assuming YOLOv5n model converted to TFLite is available at this path
MODEL_PATH = 'yolov5n.tflite'  # Update to actual model path
LABELS = ['wrench', 'screwdriver']  # Example tool labels, update as needed

def detect_tools():
    # Load TFLite model
    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Open camera (adjust index for CSI camera if needed)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            continue

        # Preprocess image for model
        input_shape = input_details[0]['shape']
        img = cv2.resize(frame, (input_shape[1], input_shape[2]))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Run inference
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()

        # Get output (assuming YOLO output format: [batch, num_boxes, 4 + num_classes])
        output = interpreter.get_tensor(output_details[0]['index'])[0]

        # Process detections (simplified, adjust based on actual model output)
        tools = []
        for detection in output:
            confidence = detection[4]  # Assuming confidence at index 4
            if confidence > 0.5:  # Threshold
                class_id = np.argmax(detection[5:])  # Class probabilities
                x, y, w, h = detection[:4]  # Bounding box
                tools.append({
                    "name": LABELS[class_id],
                    "x": int(x),
                    "y": int(y)
                })

        # Prepare result
        timestamp = datetime.datetime.now().isoformat()
        result = {
            "timestamp": timestamp,
            "tools": tools
        }
        print(json.dumps(result))  # Publish to websocket topic later

        time.sleep(2)

    cap.release()
