from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# store online users
users = {}

# ================= ROUTES =================

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/chat', methods=['POST'])
def chat():
    email = request.form.get("email")
    session['email'] = email
    return render_template("chat.html", email=email)

# ================= SOCKET =================

@socketio.on('call_user')
def call_user(data):
    target = data['target']
    if target in users:
        emit('incoming_call', {
            'from': data['from']
        }, to=users[target])

@socketio.on('webrtc_offer')
def handle_offer(data):
    target = data['to']
    if target in users:
        emit('webrtc_offer', data, to=users[target])

@socketio.on('webrtc_answer')
def handle_answer(data):
    target = data['to']
    if target in users:
        emit('webrtc_answer', data, to=users[target])

@socketio.on('ice_candidate')
def handle_ice(data):
    target = data['to']
    if target in users:
        emit('ice_candidate', data, to=users[target])

        # WEBRTC SIGNALING

        @socketio.on('webrtc_offer')
        def handle_offer(data):
            target = data['to']
            if target in users:
                emit('webrtc_offer', data, to=users[target])

        @socketio.on('webrtc_answer')
        def handle_answer(data):
            target = data['to']
            if target in users:
                emit('webrtc_answer', data, to=users[target])

        @socketio.on('ice_candidate')
        def handle_ice(data):
            target = data['to']
            if target in users:
                emit('ice_candidate', data, to=users[target])
                if __name__ == "__main__":
                    socketio.run(app, host="0.0.0.0", port=10000)