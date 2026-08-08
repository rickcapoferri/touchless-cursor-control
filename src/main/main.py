import math
import time
from pathlib import Path

import cv2
import mediapipe as mp
import pyautogui

from clap_control import DoubleClapControl

pyautogui.PAUSE = 0


MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

drawing_utils = mp.tasks.vision.drawing_utils
drawing_styles = mp.tasks.vision.drawing_styles
hand_connections = mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
LEFT_DRAG_HOLD_DELAY = 0.25


def main():
    if not MODEL_PATH.exists():
        print(f"Missing model file: {MODEL_PATH}")
        return

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Could not open the webcam.")
        return

    previous_time = 0
    mouse_is_down = False
    clap_control = DoubleClapControl()
    right_click_pinch_active = False
    left_pinch_active = False
    left_pinch_start_time = 0.0

    try:
        clap_control.start()
        print("Double clap to turn hand controls on or off.")
    except Exception as error:
        print(f"Could not start the microphone: {error}")
        print("Hand controls will remain on.")
        clap_control.set_enabled(True)

    try:
        with HandLandmarker.create_from_options(options) as landmarker:
            previous_x, previous_y = pyautogui.position()
            while True:
                success, img = cap.read()

                if not success:
                    break

                img = cv2.flip(img, 1)

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=img_rgb,
                )

                timestamp_ms = time.monotonic_ns() // 1_000_000

                results = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms,
                )

                controls_enabled = clap_control.is_enabled()

                if not controls_enabled and mouse_is_down:
                    pyautogui.mouseUp(button="left")
                    mouse_is_down = False

                if results.hand_landmarks:
                    hand_landmarks = results.hand_landmarks[0]

                    if controls_enabled:
                        previous_x, previous_y = move_cursor(
                            hand_landmarks,
                            previous_x,
                            previous_y,
                        )

                        right_click_pinching = is_right_click_pinching(
                            hand_landmarks
                        )

                        if right_click_pinching and mouse_is_down:
                            pyautogui.mouseUp(button="left")
                            mouse_is_down = False

                        right_click_pinch_active = right_click_mouse(
                            hand_landmarks,
                            right_click_pinch_active,
                        )

                        if not right_click_pinch_active:
                            (
                                mouse_is_down,
                                left_pinch_active,
                                left_pinch_start_time,
                            ) = drag_click_mouse(
                                hand_landmarks,
                                mouse_is_down,
                                left_pinch_active,
                                left_pinch_start_time,
                            )

                    height, width, _ = img.shape

                    for landmark_id, landmark in enumerate(hand_landmarks):
                        cx = int(landmark.x * width)
                        cy = int(landmark.y * height)

                        if landmark_id in (4, 8, 12, 16, 20):
                            cv2.circle(
                                img,
                                (cx, cy),
                                15,
                                (255, 0, 255),
                                cv2.FILLED,
                            )

                    drawing_utils.draw_landmarks(
                        img,
                        hand_landmarks,
                        hand_connections,
                        drawing_styles.get_default_hand_landmarks_style(),
                        drawing_styles.get_default_hand_connections_style(),
                    )
                else:
                    if mouse_is_down:
                        pyautogui.mouseUp(button="left")
                        mouse_is_down = False

                    right_click_pinch_active = False
                    previous_x, previous_y = pyautogui.position()

                if not controls_enabled:
                    right_click_pinch_active = False
                    previous_x, previous_y = pyautogui.position()

                current_time = time.perf_counter()

                if previous_time == 0:
                    fps = 0
                else:
                    fps = 1 / (current_time - previous_time)

                previous_time = current_time

                cv2.putText(
                    img,
                    f"FPS: {int(fps)}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    3,
                    (0, 255, 0),
                    3,
                )

                status_text = "HANDS ON" if controls_enabled else "HANDS OFF"
                status_color = (0, 255, 0) if controls_enabled else (0, 0, 255)

                cv2.putText(
                    img,
                    status_text,
                    (10, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    status_color,
                    2,
                )

                cv2.imshow("Hand Landmarker", img)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        if mouse_is_down:
            pyautogui.mouseUp(button="left")

        clap_control.stop()
        cap.release()
        cv2.destroyAllWindows()


def is_pinching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    index_finger_tip = hand_landmarks[8]

    distance = math.hypot(
        index_finger_tip.x - thumb_tip.x,
        index_finger_tip.y - thumb_tip.y,
    )

    return distance < 0.05


def is_right_click_pinching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    ring_tip = hand_landmarks[16]

    distance = math.hypot(
        ring_tip.x - thumb_tip.x,
        ring_tip.y - thumb_tip.y,
    )

    return distance < 0.05


def right_click_mouse(hand_landmarks, right_click_pinch_active):
    right_click_pinching = is_right_click_pinching(hand_landmarks)

    # Click only when the gesture begins.
    if right_click_pinching and not right_click_pinch_active:
        pyautogui.rightClick()

    return right_click_pinching


def move_cursor(hand_landmarks, previous_x, previous_y):
    hand_cursor = hand_landmarks[9]
    scale = 1.5
    smoothing = 0.50

    mapped_x = (hand_cursor.x - 0.5) * scale + 0.5
    mapped_y = (hand_cursor.y - 0.5) * scale + 0.5

    mapped_x = max(0.0, min(1.0, mapped_x))
    mapped_y = max(0.0, min(1.0, mapped_y))

    target_x = mapped_x * (SCREEN_WIDTH - 4) + 2
    target_y = mapped_y * (SCREEN_HEIGHT - 4) + 2

    smooth_x = previous_x + (target_x - previous_x) * smoothing
    smooth_y = previous_y + (target_y - previous_y) * smoothing

    pyautogui.moveTo(int(smooth_x), int(smooth_y))

    return smooth_x, smooth_y


def drag_click_mouse(
    hand_landmarks,
    mouse_is_down,
    left_pinch_active,
    left_pinch_start_time,
):
    pinching = is_pinching(hand_landmarks)
    current_time = time.monotonic()

    if pinching:
        if not left_pinch_active:
            left_pinch_active = True
            left_pinch_start_time = current_time

        pinch_duration = current_time - left_pinch_start_time

        if pinch_duration >= LEFT_DRAG_HOLD_DELAY and not mouse_is_down:
            pyautogui.mouseDown(button="left")
            return True, left_pinch_active, left_pinch_start_time

        return mouse_is_down, left_pinch_active, left_pinch_start_time

    if left_pinch_active:
        pinch_duration = current_time - left_pinch_start_time

        if mouse_is_down:
            pyautogui.mouseUp(button="left")
        elif pinch_duration < LEFT_DRAG_HOLD_DELAY:
            pyautogui.click(button="left")

    return False, False, 0.0


if __name__ == "__main__":
    main()
