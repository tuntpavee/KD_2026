from read_encoder import connect_to_arduino, read_encoders_once
from control_motor import connect_to_motors, send_motor_command
from maccanum_matrix import cal_matrix
import time
import math

# ==========================================
# 1. HARDWARE CONFIGURATION
# ==========================================
WHEEL_DIAMETER_M = 0.063
TICKS_PER_REV = 2171
METERS_PER_TICK = (math.pi * WHEEL_DIAMETER_M) / TICKS_PER_REV

print("Connecting to hardware...")
sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)
motor_slave = connect_to_motors('/dev/ttyUSB0', 115200)

if sensor_slave is None or motor_slave is None:
    print("Failed to connect to sensor or motor slave.")
    if sensor_slave: sensor_slave.close()
    if motor_slave: motor_slave.close()
    exit()

print("Successfully connected to both Arduinos!\n")

# ==========================================
# 2. MAIN CONTROL SEQUENCE
# ==========================================
try:
    target_distance = float(input("Enter target distance in meters (e.g. 1.0): "))

    robot_x = 0.0
    robot_y = 0.0
    is_moving = True

    # --- A. Lock in the Starting Line ---
    print("Reading initial encoder positions...")
    prev_ticks = None
    
    # Loop until we successfully get that first reading
    while prev_ticks is None:
        prev_ticks = read_encoders_once(sensor_slave)
        time.sleep(0.01) 

    print(f"Starting position locked at: {prev_ticks}\n")

    # --- B. Calculate and Send Motor Speeds ---
    target_vx = 0.2  # Move forward at 0.5 m/s
    target_vy = 0.0
    target_wz = 0.0

    rpm_m1, rpm_m2, rpm_m3, rpm_m4 = cal_matrix(target_vx, target_vy, target_wz)
    print(f"Target RPMs -> M1:{rpm_m1} | M2:{rpm_m2} | M3:{rpm_m3} | M4:{rpm_m4}")
    
    send_motor_command(motor_slave, "m1", rpm_m1)
    send_motor_command(motor_slave, "m2", rpm_m2)
    send_motor_command(motor_slave, "m3", rpm_m3)
    send_motor_command(motor_slave, "m4", rpm_m4)

    # --- C. The Odometry Measurement Loop ---
    while is_moving:
        encoder_data = read_encoders_once(sensor_slave)

        if encoder_data is not None:
            curr_ticks = encoder_data

            # 1. Calculate how many ticks each wheel moved since the last loop
            delta_ticks = [curr_ticks[i] - prev_ticks[i] for i in range(4)]
            
            # 2. Convert those ticks into meters traveled by each wheel
            d = [ticks * METERS_PER_TICK for ticks in delta_ticks]
            
            # 3. Apply Forward Kinematics to find the robot's movement
            delta_X = (d[0] + d[1] + d[2] + d[3]) / 4.0
            delta_Y = (-d[0] + d[1] + d[2] - d[3]) / 4.0
            
            # 4. Add the small movements to the robot's total position
            robot_x += delta_X
            robot_y += delta_Y
            
            # 5. Calculate total straight-line distance traveled
            total_distance_traveled = math.sqrt(robot_x**2 + robot_y**2)
            
            # Print live stats on a single updating line
            print(f"Pos: X={robot_x:.3f}m, Y={robot_y:.3f}m | Dist: {total_distance_traveled:.3f}m", end='\r')
            
            # 6. Check if we reached our target
            if total_distance_traveled >= target_distance:
                print(f"\n\nTarget distance of {target_distance}m reached! Stopping.")
                
                send_motor_command(motor_slave, "m1", 0)
                send_motor_command(motor_slave, "m2", 0)
                send_motor_command(motor_slave, "m3", 0)
                send_motor_command(motor_slave, "m4", 0)
                
                is_moving = False

            # Lock in the new position for the next loop
            prev_ticks = curr_ticks
        
        # Small delay to keep the CPU usage low
        time.sleep(0.01)

# ==========================================
# 3. EMERGENCY STOP & CLEANUP
# ==========================================
except KeyboardInterrupt:
    print("\n\nUser triggered Emergency Stop!")

finally:
    print("\nShutting down hardware...")
    if motor_slave:
        send_motor_command(motor_slave, "m1", 0)
        send_motor_command(motor_slave, "m2", 0)
        send_motor_command(motor_slave, "m3", 0)
        send_motor_command(motor_slave, "m4", 0)
        time.sleep(0.1) # Give the Mega time to read the stop commands
        motor_slave.close()
        
    if sensor_slave:
        sensor_slave.close()
        
    print("Safely disconnected.")