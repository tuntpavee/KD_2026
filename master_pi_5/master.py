import serial
import time

# Based on your Arduino IDE screenshot
port = "/dev/cu.usbmodem101" 
baud = 115200

try:
    # Initializing serial communication
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2) # Wait for the RP2350 to reset after connection
    print(f"Successfully connected to {port}")

    def send_cmd(text):
        # The board uses Serial.readStringUntil('\n')
        ser.write((text + '\n').encode('utf-8')) 
        # Read the 'ACK' response from the board
        response = ser.readline().decode('utf-8').strip()
        print(f"Board says: {response}")

    send_cmd("BEEP") # Test the GP22 buzzer
    send_cmd("RED")  # Test the GP23 RGB LEDs
    
except Exception as e:
    print(f"Could not open port: {e}")