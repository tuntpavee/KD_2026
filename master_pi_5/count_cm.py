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
TICKS_PER_REV = 4304
CM_PER_TICK = (math.pi * WHEEL_DIAMETER_CM) / TICKS_PER_REV

# ==========================================
# SETUP
# ==========================================
print("Connecting to hardware...")
sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)
motor_slave = connect_to_motors('/dev/ttyUSB0', 115200)

if sensor_slave is None or motor_slave is None:
    print("Failed to connect to sensor or motor slave")
    if sensor_slave: sensor_slave.close()
    if motor_slave: motor_slave.close()
    exit()

print("Successfully connected to both hardware!\n")

m1_distance_cm = 0.0
prev_ticks = None
is_moving = True

try:
    # Get user input in centimeters
    target_distance_cm = float(input("Enter target distance in cm (e.g. 20.0): "))

    # Calculate speeds based on target velocity
    target_vx = 0.2
    target_vy = 0.0
    target_wz = 0.0
    rpm_m1, rpm_m2, rpm_m3, rpm_m4 = cal_matrix(target_vx, target_vy, target_wz)
    
    # --- SPEED PROFILES ---
    cruise_rpm = abs(rpm_m1)  # The fast speed calculated by your matrix
    creep_rpm = 91            # The slow speed for the final 5 cm approach
    
    current_rpm = cruise_rpm
    print(f"Starting M1 at CRUISE speed: {current_rpm} RPM...")

    # SEND COMMAND ONCE BEFORE THE LOOP!
    send_motor_command(motor_slave, "m1", current_rpm)
    
    # ==========================================
    # MEASUREMENT LOOP
    # ==========================================
    while is_moving:
        encoder_data = read_encoders_once(sensor_slave)

        if encoder_data is not None:
            curr_ticks = encoder_data
            
            # Setup baseline on the first read
            if prev_ticks is None:
                prev_ticks = curr_ticks
                continue
                
            # Calculate distance moved by M1
            delta_m1_ticks = curr_ticks[0] - prev_ticks[0]
            m1_distance_cm += (delta_m1_ticks * CM_PER_TICK)
            
            # Calculate how far we have left to go
            distance_remaining = target_distance_cm - abs(m1_distance_cm)
            
            # Print live stats on a single updating line
            print(f"Dist: {abs(m1_distance_cm):.2f} cm | Left: {distance_remaining:.2f} cm | RPM: {current_rpm}  ", end='\r')

            # --- 1. THE DECELERATION ZONE ---
            # If we are within 5cm of the target, and still going fast, slow down!
            if distance_remaining <= 10.0 and current_rpm == cruise_rpm:
                current_rpm = creep_rpm
                # We use math.copysign to ensure if we were going backwards (-200 RPM), 
                # we creep backwards (-40 RPM) too.
                send_rpm = int(math.copysign(current_rpm, rpm_m1)) 
                send_motor_command(motor_slave, "m1", send_rpm)
            
            # --- 2. THE STOP CONDITION ---
            # Check if we hit or passed the target
            if abs(m1_distance_cm) >= target_distance_cm:
                print(f"\n\nTarget distance of {target_distance_cm} cm reached! Stopping.")
                
                # Stop the motor instantly
                send_motor_command(motor_slave, "m1", 0)
                is_moving = False
                
            prev_ticks = curr_ticks
        
        # A tiny sleep keeps the CPU from maxing out at 100%
        time.sleep(0.01)

# ==========================================
# CLEANUP
# ==========================================
except KeyboardInterrupt:
    print("\n\nUser exit triggered.")
finally:
    print("\nShutting down hardware...")
    if motor_slave:
        send_motor_command(motor_slave, "m1", 0)
        send_motor_command(motor_slave, "m2", 0)
        send_motor_command(motor_slave, "m3", 0)
        send_motor_command(motor_slave, "m4", 0)
        time.sleep(0.1)
        motor_slave.close()
    if sensor_slave:
        sensor_slave.close()
    print("Disconnected safely.")