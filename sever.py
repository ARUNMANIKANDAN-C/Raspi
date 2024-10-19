from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import numpy as np
import pykinect2

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize Kinect
kinect = pykinect2.PyKinectRuntime.PyKinectRuntime(pykinect2.PyKinectV2.FrameSourceTypes_Color)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        if kinect.has_new_color_frame():
            frame = kinect.get_last_color_frame()
            frame = frame.reshape((kinect.color_frame_desc.Height, kinect.color_frame_desc.Width, 4))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
