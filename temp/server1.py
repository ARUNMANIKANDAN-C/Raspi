from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import io

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')  # Use eventlet as async mode

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use 0 for the default camera

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame')
def get_frame():
    success, frame = camera.read()
    if not success:
        return "Could not capture a frame", 500
    
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return "Could not encode the frame", 500
    
    frame_bytes = io.BytesIO(buffer)
    return Response(frame_bytes.getvalue(), mimetype='image/jpeg')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
