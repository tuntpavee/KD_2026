import math

def cal_matrix(vx, vy, wz):
    """
    Calculates Mecanum wheel RPMs based on target velocities.
    Includes proportional scaling to protect motor limits.
    """
    # --- Robot Dimensions (in Meters) ---
    r = 0.0315   # Wheel radius (63mm diameter / 2)
    L = 0.1001   # Forward distance from center to wheels
    W = 0.0940   # Sideways distance from center to wheels
    
    # --- Motor Limits ---
    MAX_RPM = 255

    # 1. Calculate raw radians per second
    # w1: Front-Left | w2: Front-Right | w3: Back-Left | w4: Back-Right
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
    
    # 3. THE NORMALIZER: Check if any wheel exceeds our maximum RPM
    max_calculated = max(abs(rpm_1), abs(rpm_2), abs(rpm_3), abs(rpm_4))
    
    if max_calculated > MAX_RPM:
        # Calculate how much we need to shrink the numbers to fit under MAX_RPM
        scale_ratio = MAX_RPM / max_calculated
        
        # Scale them all down equally to preserve the movement angle
        rpm_1 = int(round(rpm_1 * scale_ratio))
        rpm_2 = int(round(rpm_2 * scale_ratio))
        rpm_3 = int(round(rpm_3 * scale_ratio))
        rpm_4 = int(round(rpm_4 * scale_ratio))
        
        # Optional: Print a warning so you know it was scaled down
        print("  [!] Warning: Speeds scaled down to respect MAX_RPM limit.")

    return (rpm_1, rpm_2, rpm_3, rpm_4)

# --- Quick Test ---
if __name__ == "__main__":
    # Example: Move forward at 0.5 m/s
    print("\nTest 1: Forward (0.5 m/s)")
    rpms_fwd = cal_matrix(0.5, 0.0, 0.0)
    print(f"Output RPMs: {rpms_fwd}")
    
    # Example: Rotate in place at 1.0 rad/s
    print("\nTest 2: Rotate Counter-Clockwise (1.0 rad/s)")
    rpms_rot = cal_matrix(0.0, 0.0, 1.0)
    print(f"Output RPMs: {rpms_rot}")