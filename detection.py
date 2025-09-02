import cv2
import mediapipe as mp
from precision import check_alignment

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

mouse_x, mouse_y = None, None  

def update_mouse_position(x, y):
    global mouse_x, mouse_y
    mouse_x, mouse_y = x, y

def detect_and_display(frame):
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    eye_center = None

    if results.multi_face_landmarks:
        for face in results.multi_face_landmarks:
            indices = [33, 133, 159, 145]  # left eye
            xs, ys = [], []
            for i in indices:
                x = int(face.landmark[i].x * w)
                y = int(face.landmark[i].y * h)
                xs.append(x); ys.append(y)
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
            eye_center = (sum(xs)//len(xs), sum(ys)//len(ys))
            cv2.circle(frame, eye_center, 5, (255, 255, 0), -1)

    if mouse_x and mouse_y:
        dropper = (int(mouse_x * w), int(mouse_y * h))
        cv2.circle(frame, dropper, 7, (0, 0, 255), -1)

        if eye_center and check_alignment(eye_center, dropper):
            cv2.circle(frame, dropper, 8, (0, 255, 0), -1)
            cv2.putText(frame, "Aligned ✅", (eye_center[0], eye_center[1]-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            return frame, "success"
        elif eye_center:
            cv2.putText(frame, "Not Aligned ❌", (eye_center[0], eye_center[1]-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            return frame, "fail"
    return frame, None
