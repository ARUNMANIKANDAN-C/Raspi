from flask import Flask, Response, send_file
from picamera2 import Picamera2
import cv2
import io

app = Flask(__name__)

# Initialize and configure the camera
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Continuous video streaming route
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame')
def get_frame():
    # Capture a single frame for GET request
    frame = camera.capture_array()
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return "Could not encode frame", 500
    
    # Convert to bytes and send as response
    frame_bytes = io.BytesIO(buffer)
    return send_file(frame_bytes, mimetype='image/jpeg', as_attachment=False)

if __name__ == '__main__':
    # Run the app on 0.0.0.0 to make it available on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)
