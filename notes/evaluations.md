# Evaluation Notes

## Current Manual Evaluation Checklist

The checklist below is for the current implementation. Results have not yet been recorded here. Automated tests cover scrolling logic and hand assignment using synthetic landmarks; they do not establish live usability.

Record the commit, macOS and Python versions, camera, lighting, and approximate hand-to-camera distance with each session.

| Check | Expected behavior |
| --- | --- |
| Activation | Controls start off when the microphone starts; a double clap enables them. Check for accidental clicks immediately afterward. |
| Cursor reach | Reach all four screen edges from a comfortable right-hand position. |
| Left click | A brief thumb–index pinch clicks once on release. |
| Drag | Holding the pinch for at least 0.25 seconds holds the left button; opening it drops the item. Check for unintended releases. |
| Right click | Thumb–ring pinch produces one right click per gesture. |
| Scroll | Left thumb–index pinch and vertical movement scroll in the intended direction. A stationary hand produces no scrolling. |
| Scroll reset | Releasing the pinch or losing left-hand tracking stops scrolling; reacquiring the hand does not jump the page. |
| Two-hand interaction | Cursor movement and scrolling can work together; scrolling pauses while a right-hand drag is active. |
| Hand assignment | Physical hands match preview labels; showing only the left hand and pressing `L` corrects a reversed assignment. |
| Disable and quit | Disabling controls or quitting during a drag releases the left mouse button. |

## Historical Baseline — 2026-08-21

The observations below describe an earlier version. In particular, the removed lateral-scroll experiment is separate from the current left-hand vertical scrolling feature. These observations have not been revalidated against the current code.

- Project: Touchless Cursor Control
- Date: 2026-08-21
- Test setup: macOS laptop, front-facing webcam, single hand, normal desk use
- Control toggle: double clap
- Cursor smoothing: `0.50`
- Cursor scale: `1.5`
- Left pinch threshold: `0.5`
- Right pinch threshold: `0.5`
- Drag hold delay: `0.25 s`
- Hand detection confidence: `0.5`
- Hand presence confidence: `0.5`
- Tracking confidence: `0.5`
- Clap threshold: `0.35`
- Clap release threshold: `0.12`

### Observed Errors

- Immediate click events can happen right after the clap gesture.
  - Possible fix: wait about `1 second` before enabling controls after the clap.

- Moving and resizing windows is not always reliable.
  - Likely cause: drag is still sensitive to small gesture changes.

- The lateral scroll experiment lagged and behaved poorly.
  - Decision: remove scrolling for now to keep the system stable.

- Clicking near the screen edges is less reliable.
  - Likely cause: mapping and safety margins near the desktop boundaries.

- When the hand is not straight or stable, accidental clicks can happen.
  - Likely cause: camera limitations and hand pose variation, not only code.

### Notes

- Right click currently uses thumb + ring finger.
- Left click uses thumb + index finger.
- Drag is based on holding the left pinch long enough before releasing.
- For the cleanest testing, show only one hand at a time to the camera.

### Fix Candidates at the Time

1. Add a short activation delay after the clap.
2. Improve drag stability.
3. Reduce false clicks near screen edges.
4. Test whether the right pinch threshold should be slightly stricter.
