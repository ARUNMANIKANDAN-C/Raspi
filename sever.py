from flask import Flask, render_template, Response, send_file
import cv2
import io

app = Flask(__name__)

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
    return send_file(frame_bytes, mimetype='image/jpeg', as_attachment=False)

if __name__ == '__main__':
    # Run the app on 0.0.0.0 to make it available on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)
