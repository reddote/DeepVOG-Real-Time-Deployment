import zmq
import cv2
import time

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.PUSH)  # PUSH socket for streaming frames
socket.bind("tcp://localhost:5550")  # Use the desktop's IP

# Poller setup
poller = zmq.Poller()
poller.register(socket, zmq.POLLOUT)  # Monitor the socket for send readiness


def send_info(pupil_info, attent_id):
    # # Compress the frame using JPEG
    # (center_x, center_y) = pupil_info0[0]  # Center of the ellipse
    # (major_axis, minor_axis) = pupil_info0[1]  # Major and minor axis lengths
    # angle = pupil_info0[2]  # Rotation angle of the ellipse

    # Prepare the message
    message = {
        'info0': pupil_info[0],  # Directly include pupil_info0
        'info1': pupil_info[1],  # Directly include pupil_info1
        'attent_id': attent_id
    }

    # Use poller to check if the socket is ready for sending
    events = dict(poller.poll(0))  # Non-blocking poll
    if socket in events and events[socket] == zmq.POLLOUT:
        # Send the message as JSON
        socket.send_json(message)
