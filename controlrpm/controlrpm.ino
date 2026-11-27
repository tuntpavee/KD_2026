#include <Wire.h>
#include "QGPMaker_MotorShield.h"
#include "QGPMaker_Encoder.h"

// --- Custom M4 Hardware Hack Pins ---
#define M4_INA A0
#define M4_INB A1
#define M4_ENA_PORT 0 

QGPMaker_MotorShield AFMS = QGPMaker_MotorShield();

// Motors
QGPMaker_DCMotor *Motor1 = AFMS.getMotor(1);
QGPMaker_DCMotor *Motor2 = AFMS.getMotor(2);
QGPMaker_DCMotor *Motor3 = AFMS.getMotor(3);

// Encoders
QGPMaker_Encoder Encoder1(1);
QGPMaker_Encoder Encoder2(2);
QGPMaker_Encoder Encoder3(3); 
QGPMaker_Encoder Encoder4(4); 

// --- PID & Telemetry Variables ---
const float COUNTS_PER_REV = 4320.0; // CHANGE THIS TO YOUR MOTOR'S CPR

// Target RPMs (Initial test values you provided)
float target_rpm[4]  = {50.0, 50.0, 50.0, 50.0}; 
float current_rpm[4] = {0.0, 0.0, 0.0, 0.0};
int   current_pwm[4] = {0, 0, 0, 0}; 

// --- AUTOTUNED PID CONSTANTS ---
// Arrays ordered by motor index: {M1, M2, M3, M4}
float Kp[4] = {6, 6, 6, 6};  
float Ki[4] = {0.0, 0.0, 0.0, 0.0}; 
float Kd[4] = {0.0, 0.0, 0.0, 0.0};  

// State variables for PID calculations
long prevPosition[4] = {0, 0, 0, 0};
float eIntegral[4] = {0, 0, 0, 0};
float ePrev[4] = {0, 0, 0, 0};

// Timing variables
unsigned long lastSendTime = 0;
unsigned long lastPidTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10); 
  
  AFMS.begin(50); 

  pinMode(M4_INA, OUTPUT);
  pinMode(M4_INB, OUTPUT);
  AFMS.setPWM(M4_ENA_PORT, 0); 

  Encoder1.write(0);
  Encoder2.write(0);
  Encoder3.write(0);
  Encoder4.write(0);

  Serial.println("INIT");
  delay(1000); 
}

void loop() {
  // 1. Listen for target RPM commands
  checkSerialCommands();
  
  // 2. Run the PID loop every 20ms
  unsigned long now = millis();
  if (now - lastPidTime >= 20) {
    updatePID(now - lastPidTime);
    lastPidTime = now;
  }
  
  // 3. Send Telemetry to Pi every 50ms
  if (now - lastSendTime >= 50) {
    lastSendTime = now;
    Serial.print("<");
    for (int i = 0; i < 4; i++) {
      Serial.print(current_rpm[i]); 
      Serial.print(",");
      Serial.print(current_pwm[i]);
      if (i < 3) Serial.print(","); 
    }
    Serial.println(">"); 
  }
}

// --- PID Controller Function ---
void updatePID(unsigned long dt) {
  long pos[4];
  
  // Read encoders. 
  // M3 and M4 are INVERTED (-) to match physical forward rotation
  pos[0] =  Encoder1.read();
  pos[1] =  Encoder2.read();
  pos[2] = -Encoder3.read(); 
  pos[3] = -Encoder4.read(); 

  // --- THE FIX: Convert milliseconds to seconds for accurate PID math ---
  float dt_sec = dt / 1000.0;

  for (int i = 0; i < 4; i++) {
    if (target_rpm[i] == 0) {
      applyRawPWM(i + 1, 0);
      eIntegral[i] = 0;
      ePrev[i] = 0;
      prevPosition[i] = pos[i];
      current_rpm[i] = 0.0;
      current_pwm[i] = 0;
      continue;
    }

    // 1. Calculate actual RPM (Keep dt in ms for the RPM formula)
    long deltaPos = pos[i] - prevPosition[i];
    prevPosition[i] = pos[i];
    current_rpm[i] = ((float)deltaPos / COUNTS_PER_REV) * (60000.0 / dt);

    // 2. Calculate Error
    float error = target_rpm[i] - current_rpm[i];

    // 3. Calculate Integral (Using dt_sec)
    eIntegral[i] += error * dt_sec;
    eIntegral[i] = constrain(eIntegral[i], -5000, 5000); // Anti-windup limit

    // 4. Calculate Derivative (Using dt_sec)
    float derivative = (error - ePrev[i]) / dt_sec;
    ePrev[i] = error;

    // 5. Compute Output
    float u = (Kp[i] * error) + (Ki[i] * eIntegral[i]) + (Kd[i] * derivative);
    
    // --- Prevent Active Braking / Reversing ---
    if (target_rpm[i] > 0) {
      // If moving forward, only allow 0 to 255
      current_pwm[i] = constrain((int)u, 0, 255);
    } else if (target_rpm[i] < 0) {
      // If moving backward, only allow -255 to 0
      current_pwm[i] = constrain((int)u, -255, 0);
    }

    // Apply to hardware
    applyRawPWM(i + 1, current_pwm[i]);
  }
}

// --- Serial Parsing Function ---
void checkSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 

    int colonIndex = command.indexOf(':');
    
    if (colonIndex != -1) {
      String motorID = command.substring(0, colonIndex); 
      float rpmValue = command.substring(colonIndex + 1).toFloat(); 

      if (motorID == "m1") target_rpm[0] = rpmValue;
      else if (motorID == "m2") target_rpm[1] = rpmValue;
      else if (motorID == "m3") target_rpm[2] = rpmValue;
      else if (motorID == "m4") target_rpm[3] = rpmValue;
    }
  }
}

// --- Motor Hardware Routing ---
void applyRawPWM(int motorNum, int speedValue) {
  uint8_t direction = (speedValue >= 0) ? FORWARD : BACKWARD;
  int absSpeed = abs(speedValue);

  switch (motorNum) {
    case 1:
      Motor1->setSpeed(absSpeed);
      Motor1->run(direction);
      break;
    case 2:
      Motor2->setSpeed(absSpeed);
      Motor2->run(direction);
      break;
    case 3:
      Motor3->setSpeed(absSpeed);
      Motor3->run(direction);
      break;
    case 4:
      DCMotor_4_Custom(speedValue); 
      break;
  }
}

// --- Custom Motor 4 Control Function ---
void DCMotor_4_Custom(int pwmValue) {
  if (pwmValue >= 0) {
    digitalWrite(M4_INA, HIGH);
    digitalWrite(M4_INB, LOW);
  } else {
    digitalWrite(M4_INA, LOW);
    digitalWrite(M4_INB, HIGH);
  }

  int shieldPWM = map(abs(pwmValue), 0, 255, 0, 4096);
  AFMS.setPWM(M4_ENA_PORT, shieldPWM);
}