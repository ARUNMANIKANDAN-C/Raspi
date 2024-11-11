from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import io

app = Flask(__name__)
socketio = SocketIO(app)

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

            # Yield the frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    # Display the streaming webpage
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # Video streaming route
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame')
def get_frame():
    # Capture a single frame
    success, frame = camera.read()
    if not success:
        return "Could not capture a frame", 500
    
    # Encode the frame as JPEG
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return "Could not encode the frame", 500
    
    # Convert to bytes and send as response
    frame_bytes = io.BytesIO(buffer)
    return Response(frame_bytes.getvalue(), mimetype='image/jpeg')

# Define a simple Socket.IO event
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('message', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Run the app with Socket.IO support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
