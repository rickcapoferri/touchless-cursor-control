import math


def select_hands(results, left_label="Right"):
    """Select physical hands from horizontally mirrored Tasks API input."""
    hands = {}
    scores = {}
    for landmarks, categories in zip(results.hand_landmarks, results.handedness):
        if not categories:
            continue
        category = categories[0]
        # Tasks API labels reverse when the camera image is mirrored.
        right_label = "Left" if left_label == "Right" else "Right"
        name = {left_label: "Left", right_label: "Right"}.get(category.category_name)
        if name is not None and category.score >= 0.75:
            if category.score > scores.get(name, 0):
                hands[name] = landmarks
                scores[name] = category.score
    return hands


def pinch_ratio(landmarks):
    width = math.hypot(landmarks[5].x - landmarks[17].x,
                       landmarks[5].y - landmarks[17].y)
    if width < 0.02:
        return None
    return math.hypot(landmarks[4].x - landmarks[8].x,
                      landmarks[4].y - landmarks[8].y) / width


class ScrollControl:
    def __init__(self, sensitivity=12.0, dead_zone=0.025, max_steps=8,
                 tracking_timeout=0.25, pinch_start=0.40, pinch_release=0.65):
        self.sensitivity = sensitivity  # Wheel steps per palm width of movement.
        self.dead_zone = dead_zone  # Ignore small fingertip tremors.
        self.max_steps = max_steps  # Bound a single frame's output.
        self.tracking_timeout = tracking_timeout
        self.pinch_start = pinch_start
        self.pinch_release = pinch_release
        self.reset()

    def reset(self):
        self.anchor_y = None
        self.previous_time = None
        self.remainder = 0.0
        self.active = False

    def update(self, landmarks, now, enabled=True):
        if not enabled or landmarks is None:
            self.reset()
            return 0

        ratio = pinch_ratio(landmarks)
        threshold = self.pinch_release if self.active else self.pinch_start
        if ratio is None or ratio >= threshold:
            self.reset()
            return 0

        palm_width = math.hypot(
            landmarks[5].x - landmarks[17].x,
            landmarks[5].y - landmarks[17].y,
        )
        if palm_width < 0.02:
            self.reset()
            return 0

        # Track the palm so closing the pinch does not itself move the page.
        palm_y = sum(landmarks[i].y for i in (0, 5, 9, 13, 17)) / 5
        stale = (self.previous_time is not None
                 and not 0 < now - self.previous_time <= self.tracking_timeout)
        self.previous_time = now
        self.active = True
        if self.anchor_y is None or stale:
            self.anchor_y = palm_y
            self.remainder = 0.0
            return 0

        displacement = (palm_y - self.anchor_y) / palm_width
        if abs(displacement) < self.dead_zone:
            return 0
        self.anchor_y = palm_y

        # Reject sudden landmark jumps instead of turning them into a swipe.
        if abs(displacement) > 1.5:
            self.remainder = 0.0
            return 0

        # Reversal starts a fresh stroke; old fractions must not resist it.
        if displacement * self.remainder < 0:
            self.remainder = 0.0
        amount = displacement * self.sensitivity + self.remainder
        steps = int(amount)
        self.remainder = amount - steps
        # Upward swipe -> negative wheel steps -> content moves upward.
        # Emit only from new movement; there is no momentum or queued output.
        return max(-self.max_steps, min(self.max_steps, steps))
