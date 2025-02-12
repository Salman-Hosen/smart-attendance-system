from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

# Get the current working directory
current_dir = os.getcwd()
print("Current working directory:", current_dir)

# Define the image file name
image_filename = "1901065.jpg"

# Construct the absolute path dynamically
ref_image_path = os.path.join(current_dir, image_filename)

# Check if the reference image exists
if not os.path.exists(ref_image_path):
    raise FileNotFoundError(f"Reference image '{ref_image_path}' not found.")

# Load the reference image
ref_image = cv2.imread(ref_image_path, cv2.IMREAD_GRAYSCALE)
if ref_image is None:
    raise ValueError(f"Failed to load reference image '{ref_image_path}'.")

# Simple home route for debugging
@app.route('/')
def home():
    return "Flask server is running! Visit '/process-image' to use the image processing endpoint."

def process_image(image_data):
    try:
        # Decode the base64 image data
        image_bytes = base64.b64decode(image_data)
        np_image = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_image, cv2.IMREAD_GRAYSCALE)

        # Check if the image is valid
        if img is None:
            raise ValueError("Failed to decode the image data.")

        # Use ORB (Oriented FAST and Rotated BRIEF) to detect features
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(ref_image, None)
        kp2, des2 = orb.detectAndCompute(img, None)

        # Use brute-force matching
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        # Set a match threshold (can be adjusted)
        match_threshold = 10
        return len(matches) > match_threshold

    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route('/process-image', methods=['POST'])
def process_image_endpoint():
    data = request.get_json()

    # Check if image data is provided
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    # Process the image and check for match
    result = process_image(data['image'])
    if isinstance(result, str):  # If the result is an error message
        return jsonify({"error": result}), 500

    # Return the result as a JSON response
    return jsonify({"match": result})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
