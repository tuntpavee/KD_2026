import serial
import time

def connect_to_arduino(port='/dev/ttyUSB0', baud_rate=115200):
    """
    Opens the serial port and waits for the Arduino to reboot.
    Call this ONLY ONCE at the start of your main script.
    """
    try:
        arduino = serial.Serial(port=port, baudrate=baud_rate, timeout=0.1)
        print(f"Connecting to {port}...")
        time.sleep(2)  # Give Arduino time to wake up
        arduino.reset_input_buffer() # Clear out startup junk
        print("Connected and ready.")
        return arduino
    except serial.SerialException as e:
        print(f"Connection failed: {e}")
        return None

def read_encoders_once(arduino):
    """
    Reads a single line of data from the open connection.
    Call this as fast as you want inside your main loop.
    Returns a tuple of (m1, m2, m3, m4) or None if no data is ready.
    """
    # Only try to read if there is actually data waiting
    if arduino and arduino.in_waiting > 0:
        raw_line = arduino.readline().decode('utf-8', errors='ignore').strip()
        
        if raw_line.startswith('<') and raw_line.endswith('>'):
            clean_data = raw_line[1:-1]
            string_values = clean_data.split(',')
            
            if len(string_values) == 4:
                try:
                    m1 = int(string_values[0])
                    m2 = int(string_values[1])
                    m3 = int(string_values[2])
                    m4 = int(string_values[3])
                    return (m1, m2, m3, m4)
                except ValueError:
                    pass # Ignore corrupted data
                    
    # If buffer was empty or data was corrupted, return None
    return None