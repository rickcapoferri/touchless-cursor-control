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
- Right-hand cursor and gesture control
- Left-hand pinch-and-move scrolling with two-hand tracking
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
├── scroll_control.py     # Left-hand scroll gesture and hand selection
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
- Move your right hand to control the cursor.
- The full screen maps to a smaller region toward your right in the mirrored camera preview: 40–84% of image width and 22–78% of image height. This reduces sideways travel by about 34% and vertical travel by 16% compared with the previous mapping. Tune `CURSOR_X_MIN`, `CURSOR_X_MAX`, `CURSOR_Y_MIN`, and `CURSOR_Y_MAX` in `src/main/main.py` to adjust the region.
- Pinch your right thumb and index finger to click.
- Hold the pinch while moving to drag.
- Pinch your right thumb and ring finger to right click.
- To scroll, touch your left thumb and index finger together in a relaxed pinch. Other fingers can rest naturally; no two-finger pose is required. When `LEFT: PINCHED - MOVE TO SCROLL` appears, move the pinched hand vertically. Swipe up to push the content up, down to pull it down.
- Release the pinch to reposition. Stop moving to stop immediately, with no momentum. Scrolling pauses during a right-hand drag.
- The preview shows left-hand tracking and the normalized pinch gap. A gap below 0.40 engages scrolling; opening above 0.65 releases it, preventing flicker near the activation threshold.
- If your physical left hand is labeled `Right`, show only your left hand and press `L` while the preview is focused. This calibrates hand assignment for the current session.
- Press `Q` in the camera window to quit.

## Stability Notes

- Two-hand scrolling is experimental and still needs live webcam testing. Keep hands apart and palms visible for reliable hand classification.
- Scrolling tracks the palm while the left thumb and index are pinched, accumulating fractional wheel steps for small swipes. Tune `sensitivity` in `ScrollControl` in `src/main/scroll_control.py` (default: 12 wheel steps per palm width). Actual scroll distance depends on the app and macOS settings.
- Right hand controls the cursor; left hand only scrolls. Handedness defaults to MediaPipe Tasks labels corrected for the mirrored camera image, with an `L` calibration override.
- A small dead zone (2.5% of palm width) filters tremor. Losing the hand, disabling controls, or releasing the pinch resets scrolling. Tracking gaps and sudden landmark jumps are discarded. The preview labels each detected hand to help check left/right assignment.
- Pinch detection is normalized using the distance between landmarks `5` and `17` as a hand-width reference, which makes the gesture less sensitive to camera distance.

## Technology

- Python
- MediaPipe Hand Landmarker
- OpenCV
- PyAutoGUI
- SoundDevice

The included `hand_landmarker.task` model is provided by the [MediaPipe Hand Landmarker project](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker).
