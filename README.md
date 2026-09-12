# Touchless Cursor Control

> **Status: Still improving.** This is an active work in progress, and I am continuing to test and refine the controls.

A webcam-based hand-tracking prototype that controls the macOS cursor without touching a mouse. The project uses MediaPipe for real-time hand landmarks, OpenCV for webcam input, and PyAutoGUI for desktop mouse actions.

## Current Features

- Real-time webcam hand tracking
- Cursor movement from a stable palm landmark
- Expanded camera-to-screen coordinate mapping
- Thumb-and-index pinch detection normalized by hand width
- Pinch to click
- Hold the pinch to drag
- Thumb-and-ring-finger pinch to right click
- Single-hand cursor and gesture control
- Double-clap activation to turn hand controls on and off
- Mirrored camera preview with landmark visualization and FPS

## Currently Working On

- Improving cursor smoothing and gesture reliability
- Reducing accidental clap and pinch detections
- Refining pinch thresholds using normalized distances instead of fixed absolute values

## Project Structure

```text
src/main/
├── clap_control.py       # Double-clap audio detection
├── hand_landmarker.task  # MediaPipe hand model
└── main.py               # Current application
```

## Setup

Create and activate a virtual environment from the project root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS, allow VS Code or Terminal to access the **Camera**, **Microphone**, and **Accessibility** controls under **System Settings > Privacy & Security**.

## Run

From the project root:

```bash
python src/main/main.py
```

Controls:

- Double clap to turn hand controls on or off.
- Move one hand to control the cursor.
- Pinch your thumb and index finger to click.
- Hold the pinch while moving to drag.
- Pinch your thumb and ring finger to right click.
- Press `Q` in the camera window to quit.

## Stability Notes

- Scrolling is not implemented in the current version because it reduced stability and introduced gesture conflicts.
- For the best experience, show only one hand at a time to the camera, because two hands can confuse the tracker.
- Gesture reliability is good for the current feature set.
- Pinch detection is normalized using the distance between landmarks `5` and `17` as a hand-width reference, which makes the gesture less sensitive to camera distance.

## Technology

- Python
- MediaPipe Hand Landmarker
- OpenCV
- PyAutoGUI
- SoundDevice

The included `hand_landmarker.task` model is provided by the [MediaPipe Hand Landmarker project](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker).
