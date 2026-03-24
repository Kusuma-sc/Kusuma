from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

users = {}

# ---------- ROUTES ----------

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/chat', methods=['POST'])
def chat():
    email = request.form.get("email")
    session['email'] = email
    return render_template("chat.html", email=email)

# ---------- SOCKET ----------

@socketio.on('connect')
def connect():
    if 'email' in session:
        users[session['email']] = request.sid

@socketio.on('disconnect')
def disconnect():
    if 'email' in session:
        users.pop(session['email'], None)

@socketio.on('call_user')
def call_user(data):
    target = data['target']
    if target in users:
        emit('incoming_call', {'from': data['from']}, to=users[target])

@socketio.on('webrtc_offer')
def offer(data):
    if data['to'] in users:
        emit('webrtc_offer', data, to=users[data['to']])

@socketio.on('webrtc_answer')
def answer(data):
    if data['to'] in users:
        emit('webrtc_answer', data, to=users[data['to']])

@socketio.on('ice_candidate')
def ice(data):
    if data['to'] in users:
        emit('ice_candidate', data, to=users[data['to']])

# ---------- RUN ----------

    if __name__ == "__main__":
        socketio.run(app)