from maccanum_matrix import cal_matrix
from read_encoder import connect_to_arduino
from control_motor import connect_to_motors, send_rpm_packet
import time
import math

print("Connecting to hardware...")
sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)
motor_slave = connect_to_motors('/dev/ttyUSB0', 115200) 

if sensor_slave is None or motor_slave is None:
    print("Failed to connect to sensor or motor slave.")
    if sensor_slave: sensor_slave.close()
    if motor_slave: motor_slave.close()
    exit()

vx = float(input("Enter Vx (m/s): "))
vy = float(input("Enter Vy (m/s): "))
wz = float(input("Enter Wz (rad/s): "))
time_frame = float(input("Enter Time frame (seconds): "))

rpm_m1, rpm_m2, rpm_m3, rpm_m4 = cal_matrix(vx, vy, wz)

final_x = vx * time_frame
final_y = vy * time_frame
final_theta_rad = wz * time_frame

final_theta_deg = math.degrees(final_theta_rad) 

print(f"\n--- COMMANDING MOTORS ---")
print(f"Target RPMs: M1:{rpm_m1:.1f} | M2:{rpm_m2:.1f} | M3:{rpm_m3:.1f} | M4:{rpm_m4:.1f}")

send_rpm_packet(motor_slave, rpm_m3, rpm_m4, rpm_m2, rpm_m1)

print(f"Moving for {time_frame} seconds...")
time.sleep(time_frame)

print("Stopping motors.")
send_rpm_packet(motor_slave, 0, 0, 0, 0)

print(f"\n--- THEORETICAL FINAL POSITION ---")
print(f"X (Forward): {final_x:.3f} meters")
print(f"Y (Strafe):  {final_y:.3f} meters")
print(f"Heading:     {final_theta_deg:.1f} degrees")
print(f"----------------------------------\n")

sensor_slave.close()
motor_slave.close()