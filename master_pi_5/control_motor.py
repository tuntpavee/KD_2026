import serial
import time

def connect_to_motors(port='/dev/ttyACM0', baud_rate=9600):
    """
    Opens the serial connection and waits for the Arduino to reboot.
    Call this ONLY ONCE at the start of your main script.
    """
    try:
        # timeout=0.1 prevents the script from freezing if the Arduino doesn't reply
        ser = serial.Serial(port, baud_rate, timeout=0.1)
        print(f"Connecting to motors on {port}...")
        
        # Wait for the Arduino to boot up
        time.sleep(2)
        
        # Flush any startup junk
        ser.reset_input_buffer()
        print("Motor controller ready.")
        return ser
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port}: {e}")
        return None

def send_motor_command(ser, motor, speed):
    """
    Sends a speed command to a specific motor.
    Call this as often as you want inside your main loop.
    """
    if ser is not None and ser.is_open:
        try:
            # Format the command: "m1:200\n"
            command = f"{motor}:{speed}\n"
            
            # Send the command as bytes
            ser.write(command.encode('utf-8'))
            
            # Optional: Read back the confirmation (uncomment if your Arduino sends a reply)
            # response = ser.readline().decode('utf-8').strip()
            # if response:
            #     print(f"Arduino says: {response}")
                
        except Exception as e:
            print(f"Failed to send command to {motor}: {e}")
    else:
        print("Serial connection is not open!")