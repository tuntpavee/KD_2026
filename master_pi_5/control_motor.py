import serial
import time

def connect_to_motors(port='/dev/ttyACM0', baud_rate=115200):
    """
    Opens the serial connection and waits for the Arduino to reboot.
    Call this ONLY ONCE at the start of your main script.
    """
    try:
        ser = serial.Serial(port, baud_rate, timeout=0.1)
        print(f"Connecting to motors on {port}...")
        
        time.sleep(2)
        
        ser.reset_input_buffer()
        print("Motor controller ready.")
        return ser
        
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port}: {e}")
        return None

def send_rpm_packet(ser, m1, m2, m3, m4):
    """
    Sends all 4 motor RPMs in a single, lightning-fast packet.
    Format: <m1,m2,m3,m4>
    """
    if ser is not None and ser.is_open:
        try:
            # 1. Format the packet exactly how the Arduino expects it
            # Example output: "<50.0,50.0,-50.0,-50.0>"
            packet = f"<{m1},{m2},{m3},{m4}>"
            
            # 2. Send the packet as bytes instantly
            ser.write(packet.encode('utf-8'))
            
        except Exception as e:
            print(f"Failed to send RPM packet: {e}")
    else:
        print("Serial connection is not open!")