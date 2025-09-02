import math

def check_alignment(eye_center, dropper_tip, max_distance=60):
    ex, ey = eye_center
    dx, dy = dropper_tip
    distance = math.sqrt((dx - ex)**2 + (dy - ey)**2)
    return distance < max_distance and dy < ey
