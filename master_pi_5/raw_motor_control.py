from read_encoder import connect_to_arduino, read_encoders_once
from control_motor import connect_to_motors, send_motor_command
from maccanum_matrix import cal_matrix
import serial
import time
import math

# ==========================================
# CONFIGURATION
# ==========================================
WHEEL_DIAMETER_CM = 6.3 
TICKS_PER_REV = 2171
CM_PER_TICK = (math.pi * WHEEL_DIAMETER_CM) / TICKS_PER_REV

# ==========================================
# SETUP
# ==========================================
print("Connecting to hardware...")
sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)
motor_slave = connect_to_motors('/dev/ttyACM0', 9600)
pwm = 200

if sensor_slave is None or motor_slave is None:
    print("Failed to connect to sensor or motor slave")
    if sensor_slave: sensor_slave.close()
    if motor_slave: motor_slave.close()
    exit()

print("Successfully connected to both hardware!\n")

try:
    while True:
        send_motor_command(motor_slave,"m1",pwm)
        send_motor_command(motor_slave,"m2",pwm)
        send_motor_command(motor_slave,"m3",pwm)
        send_motor_command(motor_slave,"m4",pwm)
except KeyboardInterrupt:
    send_motor_command(motor_slave,"m1",0)
    send_motor_command(motor_slave,"m2",0)
    send_motor_command(motor_slave,"m3",0)
    send_motor_command(motor_slave,"m4",0)
    exit()