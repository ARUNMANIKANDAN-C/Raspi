from flask import Flask, render_template, Response, jsonify, send_file
from flask_socketio import SocketIO, emit
import cv2
import base64
import io
import time
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app)  # Initialize SocketIO with Flask

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use 0 for the default camera

def generate_frames():
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Emit the frame to the client in base64 format
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('new_frame', {'frame': frame_base64})

            # Yield the frame in byte format for the video stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Optional: add delay for demonstration
            time.sleep(0.1)  # Add a short delay if needed for performance

@app.route('/')
def index():
    # Display the streaming webpage
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Video streaming route for compatibility with <img> tags if needed
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame', methods=['GET'])
def get_frame():
    # Capture a single frame
    success, frame = camera.read()
    if success:
        # Convert the frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_io = io.BytesIO(buffer)

        # Send the frame as a downloadable image
        return send_file(frame_io, mimetype='image/jpeg', as_attachment=True, download_name='frame.jpg')
    else:
        return "Failed to capture frame", 500

if __name__ == '__main__':
    # Run the app with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
