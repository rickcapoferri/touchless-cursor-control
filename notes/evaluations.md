# Evaluation Notes

## Baseline

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

## Observed Errors

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

## Notes

- Right click currently uses thumb + ring finger.
- Left click uses thumb + index finger.
- Drag is based on holding the left pinch long enough before releasing.
- For the cleanest testing, show only one hand at a time to the camera.

## Next Fix Candidates

1. Add a short activation delay after the clap.
2. Improve drag stability.
3. Reduce false clicks near screen edges.
4. Test whether the right pinch threshold should be slightly stricter.
