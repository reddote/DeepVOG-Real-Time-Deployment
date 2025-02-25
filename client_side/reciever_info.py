import zmq

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.PULL)  # PULL socket to receive frames
socket.connect("localhost:5550")  # Connect to sender's address


def receive_info():
    while True:
        try:
            # TODO the information scaled to network target size(320,240). Need to scale original image size
            # Receive JSON data from the sender
            message = socket.recv_json()
            # id = message['attent_id']
            # Extract data from the received message
            center_x = message['x']
            center_y = message['y']
            major_axis = message['w']
            minor_axis = message['h']
            angle = message['angle']

            # Print the received data
            print(f"Received Ellipse Data:")
            # print(f"id: {id}\n")
            print(f"Center: ({center_x}, {center_y})")
            print(f"Major Axis Length: {major_axis}")
            print(f"Minor Axis Length: {minor_axis}")
            print(f"Angle: {angle}\n")

        except zmq.ZMQError as e:
            print(f"ZeroMQ Error: {e}")
            break


if __name__ == "__main__":
    print("Waiting for data...")
    receive_info()
