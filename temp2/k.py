from flask import Flask, render_template_string, request, redirect, url_for
import serial
import time

# Set up serial connection
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

app = Flask(__name__)

def send_command(command):
    arduino.write((command + '\n').encode())
    print(f"Sent: {command}")
    response = arduino.readline().decode().strip()
    print(f"Arduino says: {response}")
    return response

# Simple HTML with buttons
HTML = """
<!doctype html>
<title>Rocky Bridge Control</title>
<h2>Control Panel</h2>
<form action="/send" method="post">
    <button name="cmd" value="F">Forward</button>
    <button name="cmd" value="B">Backward</button>
    <button name="cmd" value="L">Left</button>
    <button name="cmd" value="R">Right</button>
    <button name="cmd" value="S">Stop</button>
    <button name="cmd" value="SWEEP">Sweep Servo</button>
</form>
<p>Last command: {{ response }}</p>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML, response="None")

@app.route('/send', methods=['POST'])
def send():
    command = request.form['cmd']
    response = send_command(command)
    return render_template_string(HTML, response=response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
