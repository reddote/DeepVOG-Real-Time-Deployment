# DeepVOG Real-Time Project

## Overview

DeepVOG is a deep learning-based eye-tracking system designed for real-time pupil tracking. This project enables real-time tracking of eye movements using distributed systems and a deep learning model optimized for high-speed applications.

## Features

- **Real-time pupil tracking** using deep learning models
- **Optimized for high-speed cameras** (Pupil Labs cameras)
- **Uses PyTorch and OpenCV** for image processing
- **Supports GPU acceleration** via CUDA
- **Can integrate with other vision-based applications**

## Installation

To set up the environment, use Conda:

```bash
conda create -n myenv39 python=3.9 -y
conda activate myenv39
```

### Install Dependencies

```bash
conda install -c conda-forge numpy scipy pandas matplotlib opencv pytorch torchvision torchaudio
pip install mediapipe face-alignment
```

### GPU Acceleration (Optional)

If you have a compatible NVIDIA GPU, install CUDA toolkit:

```bash
conda install -c nvidia cudatoolkit=11.3
```

## Usage

1. Activate the environment:
   ```bash
   conda activate myenv39
   ```
2. Run the main script:
   ```bash
   python main.py
   ```
3. For debugging and visualization, enable logging:
   ```bash
   python main.py --debug
   ```

## Project Structure

```
DeepVOG-RealTime/
│-- deepvog/model/      # Pre-trained models
│-- client_side/        # Scripts need to run in client
│-- server_side/        # Scripts need to run in server
│-- pupil_labs_plugin/  # Pupil labs plugin implementation, check docs in this folder
│-- requirements.txt    # List of dependencies
│-- README.md           # Project documentation
```

## Troubleshooting

- **Issue: Model runs slowly**
  - Ensure you are using **CUDA-enabled PyTorch** (`torch.cuda.is_available()` should return `True`).
- **Issue: Dependencies missing**
  - Run `pip install -r requirements.txt`.
- **Issue: Camera not detected**
  - Check OpenCV installation (`cv2.VideoCapture(0)` should work).
  - If you are using Pupil Labs camera check the Pupil Capture program.


## License
This project is licensed under the GNU General Public License v3.0 (GNU GPLv3) License.