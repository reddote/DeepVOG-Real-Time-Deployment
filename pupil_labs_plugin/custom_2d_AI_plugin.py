import logging
import cv2
import numpy as np

from pupil_detectors import Detector2D, DetectorBase, Roi
from pyglui import ui

from methods import normalize

from pupil_detector_plugins import PupilDetectorPlugin
from pupil_detector_plugins.detector_base_plugin import (
    DetectorPropertyProxy,
    PupilDetectorPlugin,
)
from pupil_detector_plugins.visualizer_2d import draw_pupil_outline
import zmq

# ZeroMQ Context and Socket
context = zmq.Context()
socket = context.socket(zmq.PULL)  # PULL socket to receive frames
socket.connect("tcp://localhost:5550")  # Connect to sender's address

# Poller setup
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

logger = logging.getLogger(__name__)

pupil_information_eye0 = None
pupil_information_eye1 = None

center_x = 0
center_y = 0
major_axis = 0
minor_axis = 0
angle = 0


class CustomDetector(PupilDetectorPlugin):
    uniqueness = "by_class"
    icon_font = "pupil_icons"
    icon_chr = chr(0xEC18)

    label = "Custom Detector"

    # Use the same identifier as the built-in 2D pupil detector
    identifier = "2d"
    order = 0.9

    @property
    def pretty_class_name(self):
        return "Custom Detector"

    @property
    def pupil_detector(self) -> DetectorBase:
        return self.__detector_2d

    def __init__(self, g_pool=None):
        super().__init__(g_pool=g_pool)
        self.__detector_2d = Detector2D({})
        self._stop_other_pupil_detectors()

    def _stop_other_pupil_detectors(self):
        plugin_list = self.g_pool.plugins

        # Deactivate other PupilDetectorPlugin instances
        for plugin in plugin_list:
            if isinstance(plugin, PupilDetectorPlugin) and plugin is not self:
                plugin.alive = False

        # Force Plugin_List to remove deactivated plugins
        plugin_list.clean()

    def detect(self, frame, **kwargs):

        result = {'ellipse': None, 'diameter': None, 'location': None, 'confidence': 0, 'id': 0, 'topic': None,
                  'method': None, 'timestamp': None, 'norm_pos': None}

        eye_id = self.g_pool.eye_id
        x, y, w, h, temp_angle = self.receive_info(eye_id)
        # x, y, w, h, temp_angle = 0, 0, 0, 0, 0
        result['ellipse'] = {'center': (x, y),
                             'axes': (w, h),
                             'angle': temp_angle}
        result['diameter'] = w  # The diameter of the circle
        result['location'] = (x, y)  # The center of the circle
        result['confidence'] = 1  # Confidence is set to 1 for now
        # print(f"eye_id: {eye_id}, information: {x}, {y}, {w}, {h} ,{temp_angle}")

        result["id"] = eye_id
        result["topic"] = f"pupil.{eye_id}.{self.identifier}"
        result["method"] = "custom-2d"
        result["timestamp"] = frame.timestamp
        if result['location'] is not None:
            result["norm_pos"] = normalize(result["location"], (frame.width, frame.height), flip_y=True)

        ##with open(r'C:\Users\L1303\Desktop\pupilSource\output.txt', 'w') as f:
          ##  f.write(str(result))

        return result

    def receive_info(self, id):
        global center_x
        global center_y
        global major_axis
        global minor_axis
        global angle
        global pupil_information_eye0
        global pupil_information_eye1

        # Ensure we always return a tuple, even if no data is received
        default_result = (0, 0, 0, 0, 0)

        pupil_information_eye0 = [(0, 0), (0, 0), 0]
        pupil_information_eye1 = [(0, 0), (0, 0), 0]
        # TODO the information scaled to network target size(320,240). Need to scale original image size
        # Original and new resolutions
        original_width, original_height = 320, 240
        new_width, new_height = 400, 400

        # Scaling factors
        scale_x = new_width / original_width
        scale_y = new_height / original_height

        # Poll the socket with a timeout of 1000ms (1 second)
        events = dict(poller.poll(0))

        if socket in events:
            # TODO When I send the data, if there is no detection, the system sends a null value.
            # TODO Therefore, if there is a loss between the first and second frame,
            # TODO I still need to provide some data to Pupil Capture.
            # TODO For that reason, I send the previous data if no new data is available,
            # TODO because the eye’s position wouldn’t change significantly in a single frame.
            # TODO I didn't work on that part so if you have better solution, please fix that part :D
            # Receive JSON data from the sender
            message = socket.recv_json()
            pupil_info0 = message["info0"]
            pupil_info1 = message["info1"]
            if id == 0:
                if pupil_info0 is not None:
                    pupil_information_eye0 = pupil_info0
                    # Extract data from the received message
                    (center_x, center_y) = pupil_info0[0]
                    center_x = center_x * scale_x
                    center_y = center_y * scale_y
                    (major_axis, minor_axis) = pupil_info0[1]
                    major_axis = major_axis * scale_y
                    minor_axis = minor_axis * scale_x
                    angle = pupil_info0[2]
                    return center_x, center_y, major_axis, minor_axis, angle
                else:
                    (center_x, center_y) = pupil_information_eye0[0]
                    center_x = center_x * scale_x
                    center_y = center_y * scale_y
                    (major_axis, minor_axis) = pupil_information_eye0[1]
                    major_axis = major_axis * scale_y
                    minor_axis = minor_axis * scale_x
                    angle = pupil_information_eye0[2]
                    return center_x, center_y, major_axis, minor_axis, angle
            if id == 1:
                if pupil_info1 is not None:
                    pupil_information_eye1 = pupil_info1
                    # Extract data from the received message
                    (center_x, center_y) = pupil_info1[0]
                    center_x = center_x * scale_x
                    center_y = center_y * scale_y
                    (major_axis, minor_axis) = pupil_info1[1]
                    major_axis = major_axis * scale_y
                    minor_axis = minor_axis * scale_x
                    angle = pupil_info1[2]
                    return center_x, center_y, major_axis, minor_axis, angle
                else:
                    # Extract data from the received message
                    (center_x, center_y) = pupil_information_eye1[0]
                    center_x = center_x * scale_x
                    center_y = center_y * scale_y
                    (major_axis, minor_axis) = pupil_information_eye1[1]
                    major_axis = major_axis * scale_y
                    minor_axis = minor_axis * scale_x
                    angle = pupil_information_eye1[2]
                    return center_x, center_y, major_axis, minor_axis, angle
        else:
            return default_result

    def init_ui(self):
        super().init_ui()
        self.menu.label = self.pretty_class_name
        self.menu_icon.label_font = "pupil_icons"
        info = ui.Info_Text("Custom 2D Pupil Detector Plugin")
        self.menu.append(info)

    def gl_display(self):
        if self._recent_detection_result:
            draw_pupil_outline(self._recent_detection_result, color_rgb=(0.3, 1.0, 0.1))
