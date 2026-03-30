import math

def get_velocities_from_position(target_x, target_y, target_theta, dt=1.0):
    curr_x = 0
    curr_y = 0
    curr_theta = 0
    dx_global = target_x - curr_x
    dy_global = target_y - curr_y
    dtheta = target_theta - curr_theta

    dx_local = dx_global * math.cos(curr_theta) + dy_global * math.sin(curr_theta)
    dy_local = -dx_global * math.sin(curr_theta) + dy_global * math.cos(curr_theta)

    vx = dx_local / dt
    vy = dy_local / dt
    wz = dtheta / dt

    return vx, vy, wz


def cal_matrix_from_position(curr_pos, target_pos, dt=1.0):
    """
    Calculates Mecanum wheel RPMs directly from current and target positions.
    curr_pos and target_pos should be tuples: (x, y, theta)
    """
    # Unpack tuples
    curr_x, curr_y, curr_theta = curr_pos
    target_x, target_y, target_theta = target_pos

    # Get the required body velocities
    vx, vy, wz = get_velocities_from_position(curr_x, curr_y, curr_theta, target_x, target_y, target_theta, dt)

    # Robot Physical Parameters (Meters)
    r = 0.0315
    L = 0.1001
    W = 0.0940
    MAX_RPM = 255

    # 1. Kinematic Equations for 4WD Mecanum
    w1 = (1/r) * (vx - vy - (L + W) * wz)
    w2 = (1/r) * (vx + vy + (L + W) * wz)
    w3 = (1/r) * (vx + vy - (L + W) * wz)
    w4 = (1/r) * (vx - vy + (L + W) * wz)

    # 2. Convert to RPM
    conversion_factor = 60 / (2 * math.pi)
    rpm_1 = int(round(w1 * conversion_factor))
    rpm_2 = int(round(w2 * conversion_factor))
    rpm_3 = int(round(w3 * conversion_factor))
    rpm_4 = int(round(w4 * conversion_factor))

    # 3. Scale down if exceeding MAX_RPM
    max_calculated = max(abs(rpm_1), abs(rpm_2), abs(rpm_3), abs(rpm_4))
    
    if max_calculated > MAX_RPM:
        scale_ratio = MAX_RPM / max_calculated
        
        # Scale them all down equally to preserve the movement trajectory
        rpm_m1 = int(round(rpm_1 * scale_ratio))
        rpm_m2 = int(round(rpm_2 * scale_ratio))
        rpm_m3 = int(round(rpm_3 * scale_ratio))
        rpm_m4 = int(round(rpm_4 * scale_ratio))
        
        print(f"  [!] Warning: Speeds scaled down to respect MAX_RPM limit. (Ratio: {scale_ratio:.2f})")

    return (rpm_1, rpm_2, rpm_3, rpm_4)

if __name__ == "__main__":
    current_position = (0.0, 0.0, 0.0)
    
    target_fwd = (1.0, 0.0, 0.0)
    print("\nTest 1: Move 1m Forward (dt = 2.0s)")
    rpms_fwd = cal_matrix_from_position(current_position, target_fwd, dt=2.0)
    print(f"Output RPMs (FL, FR, RL, RR): {rpms_fwd}")
    
    target_left = (0.0, 0.5, 0.0)
    print("\nTest 2: Strafe 0.5m Left (dt = 1.0s)")
    rpms_left = cal_matrix_from_position(current_position, target_left, dt=1.0)
    print(f"Output RPMs (FL, FR, RL, RR): {rpms_left}")

    target_complex = (1.0, -1.0, math.pi/2)
    print("\nTest 3: Complex Move to (1.0, -1.0, 90deg) (dt = 1.0s)")
    rpms_complex = cal_matrix_from_position(current_position, target_complex, dt=1.0)
    print(f"Output RPMs (FL, FR, RL, RR): {rpms_complex}")