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
                
                # Check if it's our formatted packet: <m4,m3,m2,m1>
                if line.startswith('<') and line.endswith('>'):
                    # Strip the brackets
                    clean_line = line[1:-1]
                    parts = clean_line.split(',')
                    
                    if len(parts) == 4:
                        m4 = float(parts[0])
                        m3 = float(parts[1])
                        m2 = float(parts[2])
                        m1 = float(parts[3])
                        
                        # Print the success!
                        print(f"SUCCESS -> M1: {m1:.1f} | M2: {m2:.1f} | M3: {m3:.1f} | M4: {m4:.1f}")
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