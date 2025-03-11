from flask import Flask, render_template_string, request
import serial
import time

# === Set up Serial Communication ===
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

app = Flask(__name__)

# === Function to Send Command ===
def send_command(command):
    arduino.write((command + '\n').encode())
    print(f"Sent: {command}")
    response = arduino.readline().decode().strip()
    print(f"Arduino says: {response}")
    return response if response else "No response (Check connection)"

# === HTML UI ===
HTML = """
<!doctype html>
<html lang="en">
<head>
    <title>Rocky Bridge Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f0f2f5;
            padding-top: 30px;
        }
        h2 {
            color: #333;
        }
        form {
            display: inline-block;
            margin: 10px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        button, input {
            margin: 5px;
            padding: 10px 15px;
            font-size: 16px;
            border-radius: 5px;
            border: none;
        }
        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        input[type="number"] {
            width: 100px;
        }
    </style>
</head>
<body>
    <h2>Rocky Bridge Control Panel</h2>
    <form method="POST" action="/send">
        <div>
            <button name="cmd" value="F">Forward</button>
            <button name="cmd" value="B">Backward</button>
            <button name="cmd" value="L">Left</button>
            <button name="cmd" value="R">Right</button>
            <button name="cmd" value="S">Stop</button>
        </div>
        <div style="margin-top: 15px;">
            <label>Speed (0-255):</label>
            <input type="number" name="speed" min="0" max="255" value="180">
            <button name="cmd" value="SEND_SPEED">Send Speed</button>
        </div>
        <div style="margin-top: 15px;">
            <label>Servo Angle (0-180):</label>
            <input type="number" name="angle" min="0" max="180" value="90">
            <button name="cmd" value="SEND_SERVO">Send Angle</button>
        </div>
        <div style="margin-top: 15px;">
            <button name="cmd" value="SWEEP">Sweep Servo</button>
        </div>
    </form>
    <p><strong>Last command:</strong> {{ response }}</p>
</body>
</html>
"""

# === Routes ===
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML, response="None")

@app.route('/send', methods=['POST'])
def send():
    cmd = request.form['cmd']
    speed = request.form.get('speed')
    angle = request.form.get('angle')
    full_cmd = ""

    if cmd in ['F', 'B', 'L', 'R']:
        full_cmd = f"{cmd}:{speed}"
    elif cmd == 'SEND_SPEED':  # Custom send without movement
        full_cmd = f"F:{speed}"
    elif cmd == 'SEND_SERVO':
        full_cmd = f"SERVO:{angle}"
    elif cmd == 'SWEEP':
        full_cmd = "SWEEP"
    elif cmd == 'S':
        full_cmd = "S"
    else:
        full_cmd = cmd

    response = send_command(full_cmd)
    return render_template_string(HTML, response=response)

# === Run Flask App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
