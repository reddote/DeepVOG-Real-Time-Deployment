import zmq
import cv2
import time

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.PUSH)  # PUSH socket for streaming frames
socket.bind("tcp://localhost:5555")  # Use the desktop's IP

# Poller setup
poller = zmq.Poller()
poller.register(socket, zmq.POLLOUT)  # Monitor the socket for send readiness


def send_frame(frame0, frame1, attent_id):
    try:
        # Compress the frame using JPEG
        _, compressed_frame0 = cv2.imencode('.jpg', frame0)
        _, compressed_frame1 = cv2.imencode('.jpg', frame1)
        frame_bytes0 = compressed_frame0.tobytes()
        frame_bytes1 = compressed_frame1.tobytes()

        # Use poller to check if socket is ready for sending
        events = dict(poller.poll(0))  # 1-second timeout
        if socket in events and events[socket] == zmq.POLLOUT:
            print(f"sending information id: {attent_id}")
            # Send frames and attent_id as multipart message
            socket.send_multipart([
                str(attent_id).encode(),  # Convert attent_id to bytes
                frame_bytes0,
                frame_bytes1
            ])
        else:
            print("Socket not ready for sending.")
    except Exception as e:
        print(f"Error sending frames: {e}")

