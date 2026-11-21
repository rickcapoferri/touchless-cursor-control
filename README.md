# Touchless Cursor Control

> **Status: experimental prototype.** Core controls are implemented; live reliability and two-hand scrolling are still being evaluated.

A webcam-based hand-tracking prototype that controls the macOS cursor without touching a mouse. The project uses MediaPipe for real-time hand landmarks, OpenCV for webcam input, and PyAutoGUI for desktop mouse actions.

The central problem is turning noisy landmark measurements into predictable desktop actions: a small tracking error should not become an unintended click or scroll. The implementation combines geometric features, temporal smoothing, gesture state, and explicit reset behavior.

MediaPipe supplies the pretrained hand model. The application code implements the coordinate mapping, gesture rules, click/drag timing, scrolling, hand assignment, and audio activation. No custom model training is included.

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

## How It Works

```text
Webcam → MediaPipe landmarks → hand assignment → cursor / gesture logic → mouse events
Microphone → amplitude peaks + double-clap timing → controls enabled / disabled
```

### Geometric Features and Cursor Smoothing

Pinches use a dimensionless distance ratio in normalized image coordinates:

```text
pinch ratio = distance(thumb tip, finger tip) / distance(index base, little-finger base)
```

Dividing by palm width reduces sensitivity to hand size in the image and distance from the camera. It does not remove changes caused by hand rotation, occlusion, or perspective. Thumb–index and thumb–ring ratios below `0.50` trigger the right-hand click rules.

Landmark `9` supplies the cursor position. Its coordinates are mapped from a restricted camera region to the screen, clamped, and smoothed recursively:

```text
cursor[t] = cursor[t-1] + 0.50 × (mapped_position[t] - cursor[t-1])
```

Smoothing trades responsiveness for less visible jitter. The coefficient is fixed per frame, so its effective time response varies with frame rate.

### Gesture State and Scrolling

- **Click versus drag:** a pinch released before `0.25 s` clicks; holding it longer presses the mouse button until release. Elapsed time uses a monotonic clock.
- **Scroll hysteresis:** the left-hand pinch engages below `0.40` and releases at `0.65`. Separate thresholds reduce repeated toggling near the boundary.
- **Movement filtering:** scrolling follows average palm position, normalized by palm width. A dead zone suppresses small movements; fractional wheel steps accumulate to preserve small swipes.
- **Reset behavior:** hand loss, pinch release, or disabled controls resets scrolling. Gaps over `0.25 s` re-anchor movement; sudden jumps over `1.5` palm widths are discarded. Output is capped at eight wheel steps per frame.
- **Audio activation:** amplitude peaks and inter-clap timing toggle controls. This is a threshold-based detector, so other sharp sounds can trigger it.

These are hand-tuned rules, not parameters estimated from a labeled gesture dataset.

## Project Structure

```text
src/main/
├── clap_control.py       # Double-clap audio detection
├── scroll_control.py     # Left-hand scroll gesture and hand selection
├── hand_landmarker.task  # MediaPipe hand model
└── main.py               # Current application
tests/
└── test_scroll_control.py # Synthetic landmark and hand-assignment tests
notes/
└── evaluations.md        # Historical observations and manual test checklist
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

The tests cover scroll direction and magnitude, jitter rejection, hysteresis, fractional accumulation, bounded output, resets after tracking loss, and hand assignment. They also compare the same synthetic swipe sampled at two frame rates.

These tests use synthetic landmarks and require only the Python standard library. They do not verify live webcam tracking, microphone detection, desktop input, click/drag behavior, or gesture comfort. Two-hand scrolling still needs live validation. No measured accuracy, latency benchmark, or user study is reported for the current version.

See [evaluation notes](notes/evaluations.md) for the historical baseline and a checklist for testing the current controls.

### Planned Measurements

The next evaluation should record camera, lighting, hand distance, software versions, and commit alongside each session. Useful measures are false activations per minute while idle, successful clicks and drags per attempt, task completion time, and unintended scroll events. Compare raw mapping with different smoothing settings on repeated tasks to assess the jitter–responsiveness trade-off. These measurements are planned; the repository does not yet contain those results.
