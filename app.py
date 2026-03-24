from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import os

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, async_mode='threading')

# STORE USERS
users = {}

# ---------------- LOGIN ----------------
@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def userlogin():
    email = request.form['email']
    session['user'] = email
    return redirect('/chat')

# ---------------- CHAT ----------------
@app.route('/chat')
def chat():
    if 'user' in session:
        return render_template("chat.html", user=session['user'])
    return redirect('/')

# ---------------- CALL ----------------
@app.route('/call')
def call():
    if 'user' in session:
        return render_template("call.html", user=session['user'])
    return redirect('/')

# ---------------- SOCKET CONNECT ----------------
@socketio.on('connect')
def connect():
    if 'user' in session:
        users[session['user']] = request.sid

# ---------------- CHAT MESSAGE ----------------
@socketio.on('message')
def handle_message(msg):
    user = session.get('user')
    send(user + ": " + msg, broadcast=True)

# ---------------- WEBRTC SIGNALING ----------------
@socketio.on('offer')
def offer(data):
    target = data['target']
    if target in users:
        socketio.emit('offer', data, room=users[target])

@socketio.on('answer')
def answer(data):
    target = data['target']
    if target in users:
        socketio.emit('answer', data, room=users[target])

@socketio.on('candidate')
def candidate(data):
    target = data['target']
    if target in users:
        socketio.emit('candidate', data, room=users[target])

# ---------------- RUN ----------------
    import os

    if __name__ == '__main__':
        port = int(os.environ.get("PORT", 5000))
        socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)