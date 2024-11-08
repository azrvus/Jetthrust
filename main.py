from flask import Flask, jsonify
import cv2
import os
from datetime import datetime

app = Flask(__name__)

# Initialize webcam
camera = cv2.VideoCapture(0)

# Create a folder to save captured images
if not os.path.exists("captured_images"):
    os.makedirs("captured_images")

@app.route('/capture', methods=['GET'])
def capture_image():
    # Capture image from webcam
    ret, frame = camera.read()
    if not ret:
        return jsonify({"error": "Failed to capture image"}), 500

    # Create a unique filename using the current date and time
    filename = f"captured_images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # Save the captured image
    cv2.imwrite(filename, frame)

    return jsonify({"message": "Image captured successfully", "filename": filename})

@app.route('/')
def index():
    return "Welcome! Access /capture to take a picture."

if __name__ == '__main__':
    # Run Flask server on port 5000
    app.run(port=5000)
