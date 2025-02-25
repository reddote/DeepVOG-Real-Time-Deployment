import cv2
import numpy as np
import deepvog
import tensorflow as tf
from server_side.send_pupil_information import send_info

# # Print environment variables
# print("CUDA Path:", os.environ.get('PATH'))
# print("CUDA Library Path:", os.environ.get('LD_LIBRARY_PATH'))
#
# Check GPU availability
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
print("GPUs:", tf.config.list_physical_devices('GPU'))

# # Print CUDA driver version
# print(tf.sysconfig.get_build_info())

# Global model variable to ensure it is loaded only once
model = None


def load_model_once():
    """
    Load the deep learning model only once and cache it globally.
    """
    global model
    if model is None:
        print("Loading model...")
        with tf.device('/GPU:0'):  # Load model on GPU
            model = deepvog.load_DeepVOG()
        print("Model loaded successfully.")
    else:
        print("Model already loaded.")


def preprocess_input(image, target_size=(240, 320)):
    """
    Preprocess the input image to the required dimensions and normalize.
    """
    image_resized = cv2.resize(image, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)
    image_normalized = image_resized / 255.0  # Normalize to [0, 1]
    return image_normalized


def process_batch(model, frames, ids, frameID):
    """
    Process a batch of frames, predict using the model, and draw contours on each frame.
    :param model: The deep learning model.
    :param frames: List of input frames (NumPy arrays).
    :param ids: List of IDs corresponding to the frames (e.g., left or right eye).
    :param frameID: Global frame identifier for both eyes.
    :return: Combined visualization of processed frames.
    """
    # Preprocess all frames
    target_size = (240, 320)  # Target size for preprocessing
    preprocessed_frames = [preprocess_input(frame, target_size) for frame in frames]
    batch_images = np.array(preprocessed_frames)  # Combine into a single batch
    pupil_info = [None, None]

    # print(f"Processing batch with shape: {batch_images.shape}")  # Debug batch shape

    with tf.device('/GPU:0'):  # Predict on GPU
        predictions = model.predict(batch_images, batch_size=2)  # Batch prediction

    # Process predictions for each frame
    combined_images = []
    for idx, prediction in enumerate(predictions):
        frame = frames[idx]
        id = ids[idx]  # Left or right eye identifier

        # Process prediction results
        predicted_class = np.argmax(prediction, axis=-1)  # Get class with the highest probability
        prediction_image = (predicted_class * 255).astype(np.uint8)  # Convert to grayscale image format

        # Detect contours on the prediction
        contours, _ = cv2.findContours(prediction_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Resize the original frame to match the target size
        resized_frame = cv2.resize(frame, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)

        # Draw contours on the resized original frame
        frame_with_contours = resized_frame.copy()  # Create a copy to draw on
        for contour in contours:
            if len(contour) >= 5:  # Ensure there are enough points to fit an ellipse
                ellipse = cv2.fitEllipse(contour)
                # Extract width and height from the ellipse parameters
                (center, (width, height), angle) = ellipse
                # Check if both dimensions are positive
                if width > 0 and height > 0:
                    cv2.ellipse(frame_with_contours, ellipse, (0, 255, 0), 2)  # Draw ellipse in green
                    pupil_info[id] = ellipse
                else:
                    print("Skipped drawing ellipse with invalid dimensions:", ellipse)

        # Convert prediction image to BGR for visualization
        prediction_bgr = cv2.cvtColor(prediction_image, cv2.COLOR_GRAY2BGR)

        # Combine resized original, prediction, and the frame with contours
        combined_image = np.hstack((resized_frame, prediction_bgr, frame_with_contours))
        combined_images.append(combined_image)

    print(f"Pupil info: {pupil_info}")
    # if pupil_info.__len__() < 1:
    #     pupil_info.append(None)
    #     pupil_info.append(None)
    # elif pupil_info.__len__() == 1:
    #     pupil_info.append(None)
    # Combine all processed images horizontally for final visualization
    send_info(pupil_info, frameID)  # Include frameID in the sent information
    return np.vstack(combined_images)


def main(frame0, frame1, frameID):
    """
    Main function to process the left and right eye frames simultaneously using the deepvog model.
    :param frame0: Input frame for the left eye (NumPy array).
    :param frame1: Input frame for the right eye (NumPy array).
    :param frameID: Global frame identifier for both eyes.
    """
    global model  # Use the global model variable
    # Ensure GPU is visible
    print(f"Processing Frame ID: {frameID}")
    print("GPUs available:", tf.config.list_physical_devices('GPU'))

    # Load the model only once
    load_model_once()

    # Frame IDs for distinguishing left and right eye
    frame_ids = [0, 1]  # 0 for left eye, 1 for right eye

    # Process the batch (frame0: left eye, frame1: right eye)
    processed_result = process_batch(model, [frame0, frame1], frame_ids, frameID)

    return processed_result

