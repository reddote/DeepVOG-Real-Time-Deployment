# Client-Side and Server-Side Communication for Pupil Data Streaming

## Overview
This documentation describes the setup and functionality of the `server_side` directories for handling and processing Pupil Labs camera data using ZeroMQ (ZMQ) for communication. The system is designed to capture frames from a camera, transmit them to a server for further processing, and receive processed pupil data in return.

## Server-Side Components
The `server_side` directory processes incoming frames and returns processed pupil data. The core components include:

### 1. **Frame Reception and Processing**
   - The `send_frame()` function from the client sends frames to `receiver.py` on the server.
   - The `receiver.py` script receives frames via ZMQ and routes them for processing.
   - The server operates in three separate threads:
     - **Frame Receiver Thread**: Captures and routes incoming frames.
     - **Display Thread**: Uses OpenCV to visualize processed frames.
     - **Main Processing Thread**: Forwards frames to the AI model for processing.

### 2. **AI Processing (prediction.py)**
   - The `prediction.py` script contains all AI-related processing functions.
   - Since DeepVOG requires frames in 240x320 resolution, incoming frames (either 400x400 or 192x192 from Pupil Capture) are resized to 204x320 before AI processing.
   - The core function handling this is `process_batch()`, which executes all processing tasks and sends the results back to the client.

### 3. **Handling Data Loss in Pupil Capture Plugin**
   - The Pupil Capture plugin has a known issue where if no detection occurs, it sends a null value.
   - To handle frame loss, the system provides previous data when no new data is available, ensuring continuity in pupil tracking.
   - This implementation may not be optimal, and improvements are welcome.

## Additional Notes
- Ensure that Pupil Capture is correctly streaming frames via ZMQ before running `pupil_lab.py`.
- If a different camera system is used, a new script must be implemented to capture frames and call `send_frame()` in `sender.py`.
- The plugin responsible for frame scaling is located in `pupil_labs_plugin`, which ensures compatibility with DeepVOG’s 320x240 input requirement.
- If a better solution exists for handling missing frame data, improvements should be made to optimize continuity in eye tracking.

For any modifications or troubleshooting, refer to the corresponding script in `client_side` and `server_side` as required.

