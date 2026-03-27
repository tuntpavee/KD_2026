import time
from read_encoder import connect_to_arduino, read_encoders_once

print("Connecting to Uno R3...")
sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)

if sensor_slave is None:
    print("Could not connect. Exiting.")
    exit()

print("\n--- PPR CALIBRATION MODE ---")
print("1. Line up the mark on your wheel with the chassis.")
print("2. Slowly spin the wheel EXACTLY one full revolution by hand.")
print("3. Look at the number below. That is your Ticks Per Revolution!\n")

try:
    while True:
        data = read_encoders_once(sensor_slave)
        
        if data is not None:
            m1, m2, m3, m4 = data
            # Printing on a single line that overwrites itself so it's easy to read
            print(f"Current Ticks -> M1: {m1} | M2: {m2} | M3: {m3} | M4: {m4}", end='\r')
            
        # A slightly longer delay so the numbers don't flicker too fast
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nTest finished. Closing port.")

finally:
    if sensor_slave:
        sensor_slave.close()