import requests
import base64

def image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_image_to_server(image_path):
    """Send base64 image to Flask server for comparison"""
    # Your Flask server URL
    url = "http://127.0.0.1:5000/process-image"

    # Convert the image to base64
    base64_image = image_to_base64(image_path)

    # Create the payload
    payload = {
        "image": base64_image
    }

    # Send POST request to Flask API
    response = requests.post(url, json=payload)

    # Print the server's response
    print("Server Response:")
    print(response.json())

if __name__ == "__main__":
    # Replace this path with the path to your test image
    test_image_path = "d:/IOT and EMBEDDED/Esp-32-ML/flask-server/1901062.jpg"
    send_image_to_server(test_image_path)
