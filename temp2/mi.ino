#include <AFMotor.h>
#include <Servo.h>

AF_DCMotor motor1(1);  // Left Top
AF_DCMotor motor2(2);  // Left Bottom
AF_DCMotor motor3(3);  // Right Bottom
AF_DCMotor motor4(4);  // Right Top

Servo myservo;
int pos = 0;
String inputString = "";

void setup() {
  Serial.begin(9600);
  motor1.setSpeed(180);
  motor2.setSpeed(180);
  motor3.setSpeed(180);
  motor4.setSpeed(180);
  myservo.attach(10); // SERVO_2 on pin 10
  Serial.println("Arduino Ready");
}

void loop() {
  // Nothing needed here. Commands handled in serialEvent.
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      handleCommand(inputString);
      inputString = "";
    } else {
      inputString += inChar;
    }
  }
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd == "F") {
    moveForward();
    Serial.println("Moving Forward");
  } else if (cmd == "B") {
    moveBackward();
    Serial.println("Moving Backward");
  } else if (cmd == "L") {
    turnLeft();
    Serial.println("Turning Left");
  } else if (cmd == "R") {
    turnRight();
    Serial.println("Turning Right");
  } else if (cmd == "S") {
    stopMotors();
    Serial.println("Stopped");
  } else if (cmd == "SWEEP") {
    sweepServo();
    Serial.println("Servo Sweeping");
  } else {
    Serial.println("Unknown Command");
  }
}

// === Movement Functions ===
void moveForward() {
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

void moveBackward() {
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void turnLeft() {
  motor1.run(BACKWARD);
  motor2.run(BACKWARD);
  motor3.run(FORWARD);
  motor4.run(FORWARD);
}

void turnRight() {
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
}

void stopMotors() {
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  motor3.run(RELEASE);
  motor4.run(RELEASE);
}

void sweepServo() {
  for (pos = 0; pos <= 180; pos++) {
    myservo.write(pos);
    delay(10);
  }
  for (pos = 180; pos >= 0; pos--) {
    myservo.write(pos);
    delay(10);
  }
}
