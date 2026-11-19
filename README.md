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

## Current Priorities

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

The current application targets macOS and uses a webcam and microphone. The setup below uses Python 3.13.

Clone the repository and enter its directory:

```bash
git clone https://github.com/rickcapoferri/touchless-cursor-control.git
cd touchless-cursor-control
```

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

Use `requirements.txt` for this project. `libraries.txt` is a broader environment snapshot containing local paths and is not a portable installation file.

On macOS, allow VS Code or Terminal to access the **Camera**, **Microphone**, and **Accessibility** controls under **System Settings > Privacy & Security**.

## Run

From the project root:

```bash
python src/main/main.py
```

### Controls

Controls start **off** when the microphone starts successfully. Double clap to enable them and check that the preview says `HANDS ON`. If microphone startup fails, the application prints an error and leaves hand controls on.

| Action | Gesture or key |
| --- | --- |
| Enable or disable hand controls | Double clap |
| Move the cursor | Move your right hand |
| Left click | Briefly pinch your right thumb and index finger, then release |
| Drag | Hold that pinch for at least 0.25 seconds, move, then release to drop |
| Right click | Pinch your right thumb and ring finger |
| Scroll | Pinch your left thumb and index finger, then move that hand vertically |
| Calibrate hand assignment | Show only your left hand and press `L` in the preview |
| Quit | Press `Q` in the preview |

A brief left-click pinch produces the click **on release**. A held pinch becomes a drag. Right click takes priority if both right-hand pinch gestures are detected.

For scrolling, the other fingers can rest naturally. When `LEFT: PINCHED - MOVE TO SCROLL` appears, swipe up to push the content up, or down to pull it down. Release the pinch to reposition. Stop moving to stop scrolling, with no momentum. Scrolling pauses during a right-hand drag.

### Cursor Mapping and Tuning

The full screen maps to a smaller region toward your right in the mirrored camera preview: 40–84% of image width and 22–78% of image height. This lets you reach the screen edges with less hand travel.

These settings currently require editing the source:

| Setting | Location | Default |
| --- | --- | --- |
| Cursor mapping region | `CURSOR_X_MIN/MAX`, `CURSOR_Y_MIN/MAX` in `src/main/main.py` | X: 0.40–0.84; Y: 0.22–0.78 |
| Cursor smoothing | `smoothing` inside `move_cursor()` in `src/main/main.py` | 0.50 |
| Hold duration before dragging | `LEFT_DRAG_HOLD_DELAY` in `src/main/main.py` | 0.25 seconds |
| Scroll sensitivity | `sensitivity` in `ScrollControl` in `src/main/scroll_control.py` | 12 wheel steps per palm width |

The preview shows the left-hand normalized pinch gap. A gap below 0.40 engages scrolling; a gap of 0.65 or greater releases it. Using separate thresholds prevents flicker near the activation point.

### Troubleshooting

| Symptom | What to check |
| --- | --- |
| Webcam does not open | Check Camera permission for the app launching Python and whether another app is using the camera. The code selects camera index `0`. |
| Preview works, but cursor does not move | Check `HANDS ON`, right-hand detection, and Accessibility permission for the app launching Python. |
| Physical left hand is labeled `Right` | Show only your left hand and press `L` while the preview is focused. Calibration lasts for the current session. |
| Left hand is detected, but scrolling does not start | Check the pinch gap in the preview, close thumb and index finger, and make sure a right-hand drag is not active. |
| Double clap does not enable controls | Check Microphone permission and terminal messages. Audio thresholds are configured in `DoubleClapControl` in `src/main/clap_control.py`. |

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

## Verification and Evaluation

Run the automated scrolling and hand-assignment checks from the project root:

```bash
python -m unittest discover -s tests -v
```

These tests use synthetic landmarks. They do not verify live webcam tracking, microphone detection, desktop input, or gesture comfort. Two-hand scrolling still needs live validation.

See [evaluation notes](notes/evaluations.md) for the historical baseline and a checklist for testing the current controls.
