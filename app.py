from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "secret123"

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kusumasc@345__",
    database="communication"
)

cursor = db.cursor()

# ---------------- LOGIN PAGE ----------------
@app.route('/')
def login():
    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("INSERT INTO users(email, password) VALUES(%s,%s)", (email, password))
    db.commit()

    return redirect('/')

# ---------------- LOGIN LOGIC ----------------
@app.route('/login', methods=['POST'])
def userlogin():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()

    if user:
        session['user'] = email
        return redirect('/chat')
    else:
        return "Login Failed"

# ---------------- CHAT PAGE ----------------
@app.route('/chat')
def chat():
    if 'user' in session:
        return render_template("chat.html", user=session['user'])
    return redirect('/')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ================= SOCKET EVENTS =================

# JOIN ROOM
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{data['user']} joined"}, room=room)

# SEND MESSAGE
@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, room=data['room'])

# ---------------- CALL SIGNALING ----------------
@socketio.on('call_user')
def call_user(data):
    emit('incoming_call', data, room=data['to'])

@socketio.on('answer_call')
def answer_call(data):
    emit('call_answered', data, room=data['to'])

@socketio.on('ice_candidate')
def ice_candidate(data):
    emit('ice_candidate', data, room=data['to'])

# ================= RUN =================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)