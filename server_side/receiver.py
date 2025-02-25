import zmq
import cv2
import numpy as np
import threading
import prediction
import queue
import time

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://localhost:5555")

# Poller setup
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

attent_id = 0
last_attent_id = -1
received_frame0 = None
received_frame1 = None
lock = threading.Lock()

# Queue for passing frames to the display thread
display_queue = queue.Queue(maxsize=10)


# ---------------------- Frame Receiver Thread ----------------------
def receive_frames_thread():
    global received_frame0, received_frame1, last_attent_id, attent_id
    print("Starting frame receiver thread...")
    while True:
        try:
            # Poll for incoming messages with a timeout

            events = dict(poller.poll(100))  # 100ms timeout to avoid infinite waiting
            if socket in events and events[socket] == zmq.POLLIN:
                # Receive multipart message
                parts = socket.recv_multipart()

                # Decode attent_id
                attent_id = int(parts[0].decode())  # Decode the first part (attent_id)

                # Decode frames from bytes
                frame0_bytes = parts[1]
                frame1_bytes = parts[2]
                frame0 = cv2.imdecode(np.frombuffer(frame0_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                frame1 = cv2.imdecode(np.frombuffer(frame1_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Handle missing frames
                if last_attent_id != -1 and attent_id != last_attent_id + 1:
                    print(f"Warning: Lost frames! Expected {last_attent_id + 1}, but got {attent_id}.")
                last_attent_id = attent_id

                # Update the received frame (use frame0 or frame1 as needed)
                with lock:
                    received_frame0 = frame0
                    received_frame1 = frame1

        except Exception as e:
            print(f"Error in receiver thread: {e}")
            break


# ---------------------- Display Thread ----------------------
def display_frames_thread():
    """
    Continuously display frames without blocking the main processing.
    """
    print("Starting display thread...")
    while True:
        try:
            frame = display_queue.get()
            if frame is None:  # Exit condition
                break

            cv2.imshow("Processed Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting display thread.")
                break
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error in display thread: {e}")
            break
    cv2.destroyAllWindows()


# ---------------------- Main Processing Thread ----------------------
def process_frames_thread():
    """
    Processes frames and adds them to the display queue.
    """
    print("Starting processing thread...")
    while True:
        try:
            with (lock):
                if (
                    received_frame0 is not None and
                    received_frame1 is not None
                ):
                    frame_copy0 = received_frame0.copy()
                    frame_copy1 = received_frame1.copy()
                else:
                    continue  # Skip if no frame is available

            # Process the frame using prediction.main()
            predicted_frame = prediction.main(frame_copy0, frame_copy1, attent_id)

            # Add the processed frame to the display queue
            if not display_queue.full():
                display_queue.put(predicted_frame)
            else:
                print("Display queue is full. Dropping frame.")
                time.sleep(0.01)  # Small delay to prevent CPU overuse
        except Exception as e:
            print(f"Error in processing thread: {e}")
            break


# ---------------------- Start Threads ----------------------
receiver_thread = threading.Thread(target=receive_frames_thread, daemon=True)
display_thread = threading.Thread(target=display_frames_thread, daemon=True)
processing_thread = threading.Thread(target=process_frames_thread, daemon=True)

print("Starting all threads...")
receiver_thread.start()
processing_thread.start()
display_thread.start()

# ---------------------- Main Loop ----------------------
try:
    while True:
        time.sleep(0.1)  # Prevent busy waiting in the main thread
except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    print("Terminating threads and context...")
    display_queue.put(None)  # Signal the display thread to stop
    receiver_thread.join(timeout=1)
    processing_thread.join(timeout=1)
    display_thread.join(timeout=1)
    context.term()
    print("All threads terminated.")
