import cv2
from flask import Flask, render_template, Response, jsonify
from concurrent.futures import ThreadPoolExecutor
import time
from threading import Thread

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)  # Adjust based on server capability

class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise Exception("Could not open video device")
        
        self.grabbed, self.frame = self.stream.read()
        if not self.grabbed:
            raise Exception("Could not read frame from video device")
        
        self.stopped = False
        time.sleep(2.0)  # Camera warm-up time
    
    def start(self):
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def update(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()
            if not self.grabbed:
                print("Warning: Could not read frame from video stream")
                break
    
    def read(self):
        return self.frame
    
    def stop(self):
        self.stopped = True
        self.thread.join()
        self.stream.release()

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while not camera.stopped:
        frame = camera.read()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            print("Warning: Frame is None")

@app.route('/video_feed')
def video_feed():
    return Response(gen(WebcamVideoStream().start()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_frame', methods=['GET'])
def get_frame():
    """Returns a single JPEG frame as a JSON response."""
    def fetch_frame():
        camera = WebcamVideoStream().start()
        frame = camera.read()
        camera.stop()
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            return {'frame': jpeg.tobytes().hex()}  # Send frame as hex string
        else:
            return {'error': 'Failed to encode frame'}, 500

    future = executor.submit(fetch_frame)
    response = future.result()
    return jsonify(response)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True, threaded=True)
    except Exception as e:
        print(f"Error starting app: {e}")
