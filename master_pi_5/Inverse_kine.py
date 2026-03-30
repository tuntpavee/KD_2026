from position_to_velocity_matrix import cal_matrix_from_position, get_velocities_from_position
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

print("\n--- ENTER TARGET POSITION ---")
target_x = float(input("Enter Target X (meters forward): "))
target_y = float(input("Enter Target Y (meters strafe left): "))
target_theta_deg = float(input("Enter Target Heading (degrees): "))
time_frame = float(input("Enter Time frame (seconds): "))
target_theta_rad = math.radians(target_theta_deg)

vx, vy, wz = get_velocities_from_position(target_x=target_x, target_y=target_y, target_theta=target_theta_rad,dt= time_frame)

print(f"Vx {vx} m/s | Vy {vy} m/s | Wz {wz} rad/s")

current_pos = (0.0, 0.0, 0.0)
target_pos = (target_x, target_y, target_theta_rad)

rpm_m1, rpm_m2, rpm_m3, rpm_m4 = cal_matrix_from_position(current_pos, target_pos, dt=time_frame)

print(f"\n--- COMMANDING MOTORS ---")
print(f"Target RPMs: M1(FL):{rpm_m1} | M2(FR):{rpm_m2} | M3(RL):{rpm_m3} | M4(RR):{rpm_m4}")

send_rpm_packet(motor_slave, rpm_m3, rpm_m4, rpm_m2, rpm_m1)

print(f"Moving to target for {time_frame} seconds...")
time.sleep(time_frame)

print("Stopping motors.")
send_rpm_packet(motor_slave, 0, 0, 0, 0)

print(f"\n--- MOVEMENT COMPLETE ---")
print(f"Expected Final X: {target_x:.3f} meters")
print(f"Expected Final Y: {target_y:.3f} meters")
print(f"Expected Heading: {target_theta_deg:.1f} degrees")
print(f"-------------------------\n")

sensor_slave.close()
motor_slave.close()