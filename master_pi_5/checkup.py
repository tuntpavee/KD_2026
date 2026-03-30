from read_encoder import connect_to_arduino
from control_motor import connect_to_motors

def checkup():
    print("Connecting to hardware...")
    sensor_slave = connect_to_arduino('/dev/ttyUSB0', 115200)
    motor_slave = connect_to_motors('/dev/ttyUSB0', 115200)

    if sensor_slave is None or motor_slave is None:
        print("Failed to connect to sensor or motor slave.")
        if sensor_slave: sensor_slave.close()
        if motor_slave: motor_slave.close()
        exit()