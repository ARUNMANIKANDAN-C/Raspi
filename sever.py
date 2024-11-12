from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64

app = Flask(__name__)
socketio = SocketIO(app)

# Video capture (0 is typically the default camera, or you can specify a video file path)
camera = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Encode the frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        
        # Emit the frame over WebSocket
        socketio.emit('video_feed', {'frame': frame_data})

@socketio.on('connect')
def connect():
    socketio.start_background_task(generate_frames)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
