from flask import Flask, render_template_string, Response, request, jsonify
import cv2
import serial
import time
import threading

app = Flask(__name__)

# === Arduino Serial Setup ===
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"[ERROR] Arduino not found: {e}")
    arduino = None

def send_command(cmd):
    if arduino:
        try:
            arduino.write((cmd + '\n').encode())
            time.sleep(0.05)
            return arduino.readline().decode().strip()
        except:
            return "Error writing to Arduino"
    return "Arduino not connected"

# === Camera Setup ===
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# === Flask Routes ===
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/joystick', methods=['POST'])
def joystick():
    data = request.json
    control_type = data.get('control')  # "move" or "servo"
    if control_type == "move":
        direction = data.get('direction')
        speed = data.get('speed', 150)
        cmd_map = {
            "UP": f"F:{speed}",
            "DOWN": f"B:{speed}",
            "LEFT": f"L:{speed}",
            "RIGHT": f"R:{speed}",
            "STOP": "S"
        }
        cmd = cmd_map.get(direction, "S")
    elif control_type == "servo":
        angle = int(data.get('angle', 90))
        cmd = f"V:{angle}"  # Servo control
    else:
        cmd = "S"
    result = send_command(cmd)
    return jsonify(status=result)

@app.route('/status')
def status():
    return jsonify(connected=bool(arduino))

# === HTML Page ===
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Rocky Bridge Dual Joystick Control</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.0/nipplejs.min.js"></script>
  <style>
    body { font-family: Arial; background: #f2f2f2; text-align: center; padding: 20px; }
    #status-bar {
      background: #333; color: white; padding: 10px;
      font-size: 18px; margin-bottom: 20px;
    }
    .layout {
      display: flex; flex-wrap: wrap; justify-content: center;
      gap: 20px;
    }
    .zone {
      width: 200px; height: 200px; background: #ddd;
      border-radius: 15px; display: flex; align-items: center; justify-content: center;
    }
    .label { margin-top: 10px; font-size: 16px; }
    #camera {
      border: 5px solid #444; border-radius: 10px;
      width: 400px; height: auto;
    }
  </style>
</head>
<body>
  <div id="status-bar">
    Arduino Status: <span id="arduino-status">Checking...</span>
  </div>

  <h2>Rocky Bridge Control Panel</h2>

  <div class="layout">
    <div>
      <div class="zone" id="move-joystick"></div>
      <div class="label">Movement</div>
    </div>
    <div>
      <div class="zone" id="servo-joystick"></div>
      <div class="label">Servo</div>
    </div>
  </div>

  <h3 style="margin-top: 40px;">Live Camera Feed</h3>
  <img src="/video_feed" id="camera">

  <script>
    const moveJoy = nipplejs.create({
      zone: document.getElementById('move-joystick'),
      mode: 'static',
      position: { left: '50%', top: '50%' },
      color: 'blue'
    });

    const servoJoy = nipplejs.create({
      zone: document.getElementById('servo-joystick'),
      mode: 'static',
      position: { left: '50%', top: '50%' },
      color: 'green'
    });

    let lastMoveDir = "";
    let lastServoAngle = 90;
    let stopTimer = null;

    function sendJoystickCommand(control, payload) {
      fetch('/joystick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ control, ...payload })
      });
    }

    function angleToSpeed(distance) {
      let speed = Math.min(255, Math.floor(distance * 3));  // scale up
      return speed < 100 ? 100 : speed;
    }

    moveJoy.on('move', function (_, data) {
      const dir = data.direction ? data.direction.angle.toUpperCase() : "STOP";
      const speed = angleToSpeed(data.distance);
      if (dir !== lastMoveDir) {
        sendJoystickCommand("move", { direction: dir, speed });
        lastMoveDir = dir;
      }
      if (stopTimer) clearTimeout(stopTimer);
      stopTimer = setTimeout(() => {
        sendJoystickCommand("move", { direction: "STOP" });
        lastMoveDir = "";
      }, 1000);
    });

    moveJoy.on('end', function () {
      sendJoystickCommand("move", { direction: "STOP" });
      lastMoveDir = "";
    });

    servoJoy.on('move', function (_, data) {
      let angle = Math.floor((data.angle.degree + 360) % 360);
      let mapped = Math.floor(angle / 2); // map 0–360 to 0–180
      if (Math.abs(mapped - lastServoAngle) >= 3) {
        sendJoystickCommand("servo", { angle: mapped });
        lastServoAngle = mapped;
      }
    });

    function updateStatus() {
      fetch('/status').then(res => res.json()).then(data => {
        const el = document.getElementById('arduino-status');
        if (data.connected) {
          el.innerText = "Connected ✅";
          el.style.color = "lightgreen";
        } else {
          el.innerText = "Disconnected ❌";
          el.style.color = "red";
        }
      });
    }

    updateStatus();
    setInterval(updateStatus, 3000);
  </script>
</body>
</html>
"""

# === Start the Server ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
