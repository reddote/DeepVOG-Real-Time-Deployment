# Client-Side and Server-Side Communication for Pupil Data Streaming

## Overview
This documentation describes the setup and functionality of the `client_side` and `server_side` directories for handling and processing Pupil Labs camera data using ZeroMQ (ZMQ) for communication. The system is designed to capture frames from a camera, transmit them to a server for further processing, and receive processed pupil data in return.

## Client-Side Components
The `client_side` directory is responsible for capturing camera frames and transmitting them to the server using ZMQ. This includes:

### 1. **Pupil Capture Integration**
   - The Pupil Capture program from Pupil Labs must be running to stream camera data over ZMQ.
   - The `pupil_lab.py` script retrieves frames from Pupil Capture and sends them to the server without modifications.
   - If Pupil Capture is not being used, a custom script must be written to capture frames and integrate with the sending script.

### 2. **Frame Transmission (sender.py)**
   - The `sender.py` script is responsible for sending frames to the server.
   - The function `send_frame(frame0, frame1, attend_id)` is used to transmit the captured frames.
   - If frames are properly captured and passed to `send_frame()`, no modifications are required on the server side for compatibility.

### 3. **Receiving Processed Data (receiver_info.py)**
   - The `receiver_info.py` script listens for processed pupil data from the server.
   - The script checks whether data has been received but does not perform scaling operations.
   - Pupil Labs provides frames in 400x400 resolution, which must be scaled to 320x240 to be compatible with DeepVOG.
   - Scaling is handled within the `pupil_labs_plugin` directory, specifically inside the plugin script responsible for preprocessing.

## Server-Side Components
The `server_side` directory processes incoming frames and returns processed pupil data. Since the transmission and receiving mechanisms are designed to work seamlessly, no modifications are required if the client-side scripts function correctly.

## Additional Notes
- Ensure that Pupil Capture is correctly streaming frames via ZMQ before running `pupil_lab.py`.
- If a different camera system is used, a new script must be implemented to capture frames and call `send_frame()` in `sender.py`.
- The plugin responsible for frame scaling is located in `pupil_labs_plugin`, which ensures compatibility with DeepVOG’s 320x240 input requirement.

For any modifications or troubleshooting, refer to the corresponding script in `client_side` and `server_side` as required.

