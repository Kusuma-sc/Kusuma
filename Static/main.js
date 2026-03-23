// -------------------------
// Connect to Socket.IO server
// -------------------------
let socket = io();
let myEmail = "";
let localStream;
let peerConnection;

// STUN server for WebRTC
const configuration = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

// -------------------------
// Join the server with email
// -------------------------
function join() {
    myEmail = document.getElementById('myEmail').value;
    socket.emit('join', { email: myEmail });
    alert("Joined as " + myEmail);
}

// -------------------------
// Make a call to another user
// -------------------------
function makeCall() {
    let callTo = document.getElementById('callToEmail').value;
    startCall(); // get microphone access first

    // Create a peer connection
    peerConnection = new RTCPeerConnection(configuration);

    // Add local audio stream to connection
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    // When remote track arrives, play it
    peerConnection.ontrack = (event) => {
        let audio = document.createElement('audio');
        audio.srcObject = event.streams[0];
        audio.autoplay = true;
        document.body.appendChild(audio);
    };

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('signal', {
                target: callTo,
                candidate: event.candidate,
                sender: myEmail
            });
        }
    };

    // Create offer
    peerConnection.createOffer()
    .then(offer => {
        peerConnection.setLocalDescription(offer);
        socket.emit('signal', {
            target: callTo,
            sdp: offer,
            sender: myEmail
        });
    })
    .catch(err => console.error(err));

    // Notify receiver about call
    socket.emit('call', { sender: myEmail, receiver: callTo });
}

// -------------------------
// Accept incoming call
// -------------------------
function acceptCall(from) {
    startCall(); // get microphone access first

    peerConnection = new RTCPeerConnection(configuration);

    // Add local audio tracks
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    // Play remote audio
    peerConnection.ontrack = (event) => {
        let audio = document.createElement('audio');
        audio.srcObject = event.streams[0];
        audio.autoplay = true;
        document.body.appendChild(audio);
    };

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('signal', {
                target: from,
                candidate: event.candidate,
                sender: myEmail
            });
        }
    };

    socket.emit('accept_call', { sender: from, receiver: myEmail });
}

// -------------------------
// Handle incoming call request
// -------------------------
socket.on('incoming_call', (data) => {
    let from = data.from;
    let div = document.getElementById('incoming');
    div.innerHTML = `Incoming call from ${from} <button onclick="acceptCall('${from}')">Accept</button>`;
});

// -------------------------
// Notify sender when call accepted
// -------------------------
socket.on('call_accepted', (data) => {
    alert("Call accepted by " + data.from);
});

// -------------------------
// Handle WebRTC signaling data
// -------------------------
socket.on('signal', async (data) => {
    if (!peerConnection) {
        // Create connection if it doesn't exist
        peerConnection = new RTCPeerConnection(configuration);
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

        peerConnection.ontrack = (event) => {
            let audio = document.createElement('audio');
            audio.srcObject = event.streams[0];
            audio.autoplay = true;
            document.body.appendChild(audio);
        };

        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                socket.emit('signal', {
                    target: data.sender,
                    candidate: event.candidate,
                    sender: myEmail
                });
            }
        };
    }

    // Handle ICE candidate
    if (data.candidate) {
        try {
            await peerConnection.addIceCandidate(data.candidate);
        } catch (err) {
            console.error(err);
        }
    }

    // Handle SDP offer
    if (data.sdp) {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.sdp));

        if (data.sdp.type === 'offer') {
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            socket.emit('signal', {
                target: data.sender,
                sdp: answer,
                sender: myEmail
            });
        }
    }
});

// -------------------------
// Access microphone
// -------------------------
function startCall() {
    return navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        localStream = stream;
        alert("Microphone access granted!");
    })
    .catch(err => {
        alert("Microphone access denied: " + err);
    });
}