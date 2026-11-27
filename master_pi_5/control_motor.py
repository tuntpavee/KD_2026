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

def send_motor_command(ser, motor_id, rpm):
    """
    Sends a target RPM for one motor.
    Format expected by controlrpm.ino: "m1:50\\n"
    """
    if ser is not None and ser.is_open:
        try:
            ser.write(f"{motor_id}:{rpm}\n".encode('utf-8'))
        except Exception as e:
            print(f"Failed to send command to {motor_id}: {e}")
    else:
        print("Serial connection is not open!")

def send_rpm_packet(ser, m1, m2, m3, m4):
    """
    Sends all 4 motor RPMs, one line per motor.
    Example output: "m1:50\\nm2:50\\nm3:-50\\nm4:-50\\n"
    """
    if ser is not None and ser.is_open:
        try:
            packet = f"m1:{m1}\nm2:{m2}\nm3:{m3}\nm4:{m4}\n"
            ser.write(packet.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send RPM packet: {e}")
    else:
        print("Serial connection is not open!")