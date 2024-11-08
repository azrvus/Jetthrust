from flask import Flask, render_template, Response
import cv2
import pyaudio
import wave
import requests
import platform
import psutil
import threading

app = Flask(__name__)

# Camera setup
cap = cv2.VideoCapture(0)

# Recording audio in background
def record_audio(filename="audio.wav", duration=10):
    p = pyaudio.PyAudio()
    rate = 44100
    chunk = 1024
    channels = 1
    format = pyaudio.paInt16

    stream = p.open(format=format, channels=channels, rate=rate,
                    input=True, frames_per_buffer=chunk)
    frames = []
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    stream.stop_stream()
    stream.close()
    p.terminate()

# Get location
def get_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        location = data.get('loc', 'Unknown location')
        return location
    except Exception as e:
        return None

# Get device details
def get_device_details():
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=True),
        "RAM": psutil.virtual_memory().total // (1024 ** 2)  # MB
    }
    return system_info

# Video streaming function
def gen_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    # Capture image from camera
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image.jpg", frame)

    # Record audio in the background
    audio_thread = threading.Thread(target=record_audio, args=("audio.wav", 10))
    audio_thread.start()

    # Get device info and location
    location = get_location()
    device_info = get_device_details()

    # Save or display data as needed
    return f"Image captured, audio recorded, Location: {location}, Device Info: {device_info}"

if __name__ == '__main__':
    app.run(debug=True)
