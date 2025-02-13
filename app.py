from flask import Flask, request, jsonify
import base64
import pickle
import numpy as np
import cv2
from deepface import DeepFace
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# ✅ Load Firebase credentials and database reference
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://attendencesytem-ce04e-default-rtdb.firebaseio.com/"})
students_ref = db.reference("students")

# ✅ Load known encodings
with open("encodings.pkl", "rb") as file:
    known_encodings, known_names = pickle.load(file)

# ✅ Store last detected student globally
last_detected = {"student_id": None, "student_data": None}

@app.route('/')
def home():
    return "ESP32 Face Recognition Server is Running!"

# ✅ Route to receive and process an image from ESP32-CAM
@app.route('/upload-image', methods=['POST'])
def upload_image():
    global last_detected
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

        # Generate face embedding for incoming image
        embedding_data = DeepFace.represent(img, model_name="Facenet", enforce_detection=True)
        if not embedding_data:
            return jsonify({"message": "No face detected"}), 400

        incoming_embedding = embedding_data[0]['embedding']

        # Compare with stored encodings
        best_match = None
        min_distance = float("inf")
        threshold = 10  # Adjust as needed

        for known_embedding, name in zip(known_encodings, known_names):
            distance = np.linalg.norm(np.array(known_embedding) - np.array(incoming_embedding))
            if distance < threshold:
                if distance < min_distance:
                    min_distance = distance
                    best_match = name

        if best_match:
            print(f"✅ Match Found: {best_match}")

            # Fetch student details from Firebase
            student_data = students_ref.child(best_match).get()
            if student_data:
                last_detected["student_id"] = best_match
                last_detected["student_data"] = student_data  # Store last detected student info

                response_data = {
                    "message": "Match found",
                    "student_id": best_match,
                    "student_data": student_data
                }
                return jsonify(response_data), 200
            else:
                return jsonify({"message": "Student data not found in Firebase"}), 404
        else:
            return jsonify({"message": "No match found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Route to get face recognition status
@app.route('/get-detection-status', methods=['GET'])
def get_detection_status():
    try:
        if last_detected["student_id"]:
            return jsonify({
                "status": "Service running",
                "last_detected": last_detected
            }), 200
        else:
            return jsonify({
                "status": "Service running",
                "message": "No recent detection"
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
