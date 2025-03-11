from flask import Flask, render_template_string, request, jsonify
import serial
import time

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"Arduino error: {e}")
    arduino = None

app = Flask(__name__)

def send_command(command):
    if arduino:
        arduino.write((command + '\n').encode())
        time.sleep(0.05)
        return arduino.readline().decode().strip()
    return "Arduino not connected"

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Rocky Bridge Joystick</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.9.0/nipplejs.min.js"></script>
  <style>
    body { font-family: Arial; text-align: center; background: #f2f2f2; }
    #joystick-zone {
      width: 300px; height: 300px;
      margin: 50px auto; background: #ddd;
      border-radius: 50%; position: relative;
    }
    p { font-size: 20px; }
  </style>
</head>
<body>
  <h2>Joystick Control</h2>
  <div id="joystick-zone"></div>
  <p><strong>Status:</strong> <span id="status">Idle</span></p>

  <script>
    const joystick = nipplejs.create({
      zone: document.getElementById('joystick-zone'),
      mode: 'static',
      position: { left: '50%', top: '50%' },
      color: 'blue'
    });

    let lastDirection = "";
    let timeout = null;

    function sendJoystickCommand(dir) {
      if (dir !== lastDirection) {
        fetch('/joystick', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ direction: dir })
        })
        .then(res => res.json())
        .then(data => {
          document.getElementById('status').innerText = data.status;
          lastDirection = dir;
        });
      }
    }

    function stopCommand() {
      lastDirection = "";
      fetch('/joystick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: 'STOP' })
      });
      document.getElementById('status').innerText = "Idle";
    }

    joystick.on('dir', function (evt, data) {
      const dir = data.direction.angle.toUpperCase();
      sendJoystickCommand(dir);
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(stopCommand, 1000);  // auto stop after 1s idle
    });

    joystick.on('end', stopCommand);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/joystick', methods=['POST'])
def joystick():
    direction = request.json.get('direction')
    speed = 180  # you can make it dynamic
    cmd_map = {
        "UP": f"F:{speed}",
        "DOWN": f"B:{speed}",
        "LEFT": f"L:{speed}",
        "RIGHT": f"R:{speed}",
        "STOP": "S"
    }
    cmd = cmd_map.get(direction, "S")
    response = send_command(cmd)
    return jsonify(status=f"{direction} → {response}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
