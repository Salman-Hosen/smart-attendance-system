from flask import Flask, request, jsonify

app = Flask(__name__)

# Predefined list of names
valid_names = ["Alice", "Bob", "Charlie", "Salman", "David"]

@app.route('/')
def home():
    return "Flask server is running! Send a POST request to '/check-name' with a JSON payload."

@app.route('/check-name', methods=['POST'])
def check_name():
    data = request.get_json()

    # Validate request
    if not data or 'name' not in data:
        return jsonify({"error": "No name provided"}), 400

    name = data['name']
    match = name in valid_names  # Check if the name exists in the list

    return jsonify({"match": match})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
