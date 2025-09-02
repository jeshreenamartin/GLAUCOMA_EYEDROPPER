from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
import cv2
from detection import detect_and_display, update_mouse_position
from database import get_db, init_db
from logging_utils import log_event
import json

app = Flask(__name__)
app.secret_key = "secret123"
camera = cv2.VideoCapture(0)

# Initialize database
init_db()

@app.route('/')
def home():
    return render_template('index.html')  # This will serve your React app

@app.route('/api/login', methods=["POST"])
def login():
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form["username"]
        password = request.form["password"]
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    
    if user:
        session["user"] = username
        return jsonify({"success": True, "username": username})
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route('/api/register', methods=["POST"])
def register():
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form["username"]
        password = request.form["password"]
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": "Username already exists!"})

@app.route('/api/check-auth')
def check_auth():
    if "user" in session:
        return jsonify({"loggedIn": True, "username": session["user"]})
    return jsonify({"loggedIn": False})

@app.route('/api/dashboard')
def dashboard():
    if "user" not in session: 
        return jsonify({"error": "Not authenticated"}), 401
    
    # Return dashboard data
    return jsonify({
        "username": session["user"],
        "medication_adherence": "92%",
        "last_application": "Today, 8:30 AM",
        "next_scheduled": "Tomorrow, 8:30 AM",
        "battery_level": "85%",
        "connected": True,
        "medication_level": "60%"
    })

@app.route('/eye-drop-app')
def eye_drop_app():
    if "user" not in session: 
        return redirect(url_for('home'))
    return render_template("eye_drop.html")

@app.route('/update_mouse', methods=["POST"])
def update_mouse():
    data = request.get_json()
    update_mouse_position(data['x'], data['y'])
    return {"status":"ok"}

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success: break
        frame, status = detect_and_display(frame)
        if status and "user" in session:
            log_event(session["user"], status)
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/logout')
def logout():
    session.pop("user", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)