# Touchless Cursor Control

> **Status: Still improving.** This is an active work in progress, and I am continuing to test and refine the controls.

A webcam-based hand-tracking prototype that controls the macOS cursor without touching a mouse. The project uses MediaPipe for real-time hand landmarks, OpenCV for webcam input, and PyAutoGUI for desktop mouse actions.

## Current Features

- Real-time webcam hand tracking
- Cursor movement from a stable palm landmark
- Expanded camera-to-screen coordinate mapping
- Thumb-and-index pinch detection
- Pinch to click
- Hold the pinch to drag
- Thumb-and-middle-finger pinch to right click
- Right-hand-only cursor and click control
- Experimental left-hand two-finger vertical scrolling
- Double-clap activation to turn hand controls on and off
- Mirrored camera preview with landmark visualization and FPS

## Currently Working On

- Improving cursor smoothing and gesture reliability
- Calibrating left-hand scroll speed and dead-zone behavior
- Reducing accidental clap and pinch detections

## Known Limitations

- Left-hand scrolling can currently interfere with the cursor position.
- Downward scrolling is not working reliably yet.

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
python3.13 -m venv .ic-env
source .ic-env/bin/activate
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
- Move your right hand to control the cursor.
- Pinch your right thumb and index finger to click.
- Hold the right-hand pinch while moving to drag.
- Pinch your right thumb and middle finger to right click.
- Hold up your left index and middle fingers to set a neutral point. Hold the hand above or below that point to scroll.
- Press `Q` in the camera window to quit.

## Technology

- Python
- MediaPipe Hand Landmarker
- OpenCV
- PyAutoGUI
- SoundDevice

The included `hand_landmarker.task` model is provided by the [MediaPipe Hand Landmarker project](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker).
