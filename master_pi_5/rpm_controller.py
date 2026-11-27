import serial
import time

print("Connecting to Arduino Uno...")

# 1. Connect to the Serial Port
try:
    sensor_slave = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
except Exception as e:
    print(f"FAILED to connect to /dev/ttyUSB0. Error: {e}")
    exit()

# 2. The Boot Delay
print("Waiting 2 seconds for Arduino to reboot...")
time.sleep(2.0)

# Flush any garbage data that built up while booting
sensor_slave.reset_input_buffer()
print("Buffer cleared. Listening for RPM data...\n")

# 3. The Infinite Listening Loop
try:
    while True:
        # Check if the Arduino has sent us anything
        if sensor_slave.in_waiting > 0:
            
            # Read a single line of data
            raw_data = sensor_slave.readline()
            
            try:
                # Try to decode it to readable text
                line = raw_data.decode('utf-8').strip()
                
                # Check if it's our formatted packet: <rpm1,pwm1,rpm2,pwm2,rpm3,pwm3,rpm4,pwm4>
                if line.startswith('<') and line.endswith('>'):
                    # Strip the brackets
                    clean_line = line[1:-1]
                    parts = clean_line.split(',')

                    if len(parts) == 8:
                        rpm = [float(parts[i]) for i in range(0, 8, 2)]
                        pwm = [int(float(parts[i])) for i in range(1, 8, 2)]

                        # Print the success!
                        print(f"SUCCESS -> M1: {rpm[0]:.1f} rpm ({pwm[0]}) | M2: {rpm[1]:.1f} rpm ({pwm[1]}) | "
                              f"M3: {rpm[2]:.1f} rpm ({pwm[2]}) | M4: {rpm[3]:.1f} rpm ({pwm[3]})")
                    else:
                        print(f"ERROR: Found brackets, but wrong number of parts. Line: {line}")
                else:
                    print(f"WARNING: Unrecognized data format -> {line}")
                    
            except Exception as e:
                print(f"CRASH: Could not decode the data. Raw bytes: {raw_data} | Error: {e}")
        
        # A tiny sleep to prevent the CPU from maxing out at 100%
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\nExiting diagnostic tool.")
finally:
    if sensor_slave:
        sensor_slave.close()
    print("Serial port closed.")