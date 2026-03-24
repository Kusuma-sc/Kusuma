import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

users = {}

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/chat", methods=["POST"])
def chat():
    email = request.form.get("email")
    session["email"] = email
    return render_template("chat.html", email=email)

# ===== USER CONNECT =====
@socketio.on("connect")
def connect():
    email = session.get("email")
    if email:
        users[email] = request.sid

@socketio.on("disconnect")
def disconnect():
    for user, sid in list(users.items()):
        if sid == request.sid:
            users.pop(user)

# ===== CALL =====
@socketio.on("call_user")
def call_user(data):
    if data["target"] in users:
        emit("incoming_call", {"from": data["from"]}, to=users[data["target"]])

# ===== WEBRTC =====
@socketio.on("webrtc_offer")
def offer(data):
    if data["to"] in users:
        emit("webrtc_offer", data, to=users[data["to"]])

@socketio.on("webrtc_answer")
def answer(data):
    if data["to"] in users:
        emit("webrtc_answer", data, to=users[data["to"]])

@socketio.on("ice_candidate")
def ice(data):
    if data["to"] in users:
        emit("ice_candidate", data, to=users[data["to"]])