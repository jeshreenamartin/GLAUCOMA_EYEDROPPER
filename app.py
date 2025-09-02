from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
import cv2
from detection import detect_and_display, update_mouse_position
from database import get_db
from logging_utils import log_event

app = Flask(__name__)
app.secret_key = "secret123"
camera = cv2.VideoCapture(0)

@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for("login"))
        except:
            return "Username already exists!"
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["user"])

@app.route('/index')
def index():
    if "user" not in session: return redirect(url_for("login"))
    return render_template("index.html")

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

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
