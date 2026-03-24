import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/chat", methods=["POST"])
def chat():
    email = request.form.get("email")
    session["email"] = email
    return render_template("chat.html", email=email)

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

@socketio.on("send_message")
def message(data):
    emit("receive_message", data, broadcast=True)