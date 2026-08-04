# Touchless Cursor Control

> **Status: Work in progress.** I am currently building and improving this project.

A webcam-based hand-tracking prototype that controls the macOS cursor without touching a mouse. The project uses MediaPipe for real-time hand landmarks, OpenCV for webcam input, and PyAutoGUI for desktop mouse actions.

## Current Features

- Real-time webcam hand tracking
- Cursor movement from a stable palm landmark
- Expanded camera-to-screen coordinate mapping
- Thumb-and-index pinch detection
- Pinch to click
- Hold the pinch to drag
- Mirrored camera preview with landmark visualization and FPS

## Currently Working On

- Detecting and distinguishing left and right hands
- Restricting cursor and click control to the right hand
- Adding left-hand scrolling gestures
- Double-clap activation to turn hand controls on and off
- Improving cursor smoothing and gesture reliability

## Project Structure

```text
src/main/
├── hand_landmarker.task  # MediaPipe hand model
└── main.py               # Current application
```

## Setup

Create and activate a virtual environment from the project root:

```bash
python3.13 -m venv .ic-env
source .ic-env/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS, allow VS Code or Terminal to access the **Camera** and **Accessibility** controls under **System Settings > Privacy & Security**.

## Run

From the project root:

```bash
python src/main/main.py
```

Controls:

- Move your hand to control the cursor.
- Pinch your thumb and index finger to click.
- Hold the pinch while moving to drag.
- Press `Q` in the camera window to quit.

## Technology

- Python
- MediaPipe Hand Landmarker
- OpenCV
- PyAutoGUI

The included `hand_landmarker.task` model is provided by the [MediaPipe Hand Landmarker project](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker).
