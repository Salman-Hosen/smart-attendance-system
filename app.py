from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2
import os

app = Flask(__name__)

object_detected = False  # Stores object detection status
current_dir = os.getcwd()
haarCascadeFile= 'haarcascade_frontalface_default.xml'
haarCascadeFile = os.path.join(current_dir, haarCascadeFile)

# Load Haar Cascade for Object Detection (Example: Face Detection)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + haarCascadeFile)

@app.route('/')
def home():
    return "ESP32 Object Detection Server is Running!"

# ✅ Route to receive an image from ESP32-CAM
@app.route('/upload-image', methods=['POST'])
def upload_image():
    global object_detected
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode Base64 image
        image_data = base64.b64decode(data['image'])
        np_image = np.frombuffer(image_data, dtype=np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Invalid image data"}), 400

        # Convert to grayscale for object detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect objects (example: faces)
        objects = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(objects) > 0:
            object_detected = True
            print("✅ Object detected!")
        else:
            object_detected = False
            print("❌ No object detected.")

        return jsonify({"message": "Image received successfully","Detection":object_detected}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route to check object detection status
@app.route('/get-detection-status', methods=['GET'])
def get_detection_status():
    if object_detected:
        return jsonify({"status": "Object detected"})
    else:
        return jsonify({"status": "No object detected"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
