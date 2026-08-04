import math
import time
from pathlib import Path

import cv2
import mediapipe as mp
import pyautogui

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

    with HandLandmarker.create_from_options(options) as landmarker:
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

            if results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
                    move_cursor(hand_landmarks)
                    mouse_is_down = drag_click_mouse(
                        hand_landmarks,
                        mouse_is_down,
                    )

                    height, width, _ = img.shape

                    for landmark_id, landmark in enumerate(hand_landmarks):
                        cx = int(landmark.x * width)
                        cy = int(landmark.y * height)

                        if landmark_id in (4, 8, 12, 16, 20):
                            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                    drawing_utils.draw_landmarks(
                        img,
                        hand_landmarks,
                        hand_connections,
                        drawing_styles.get_default_hand_landmarks_style(),
                        drawing_styles.get_default_hand_connections_style(),
                    )
            elif mouse_is_down:
                pyautogui.mouseUp(button="left")
                mouse_is_down = False

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

            cv2.imshow("Hand Landmarker", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if mouse_is_down:
        pyautogui.mouseUp(button="left")

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


def move_cursor(hand_landmarks):
    hand_cursor = hand_landmarks[9]
    scale = 1.5

    mapped_x = (hand_cursor.x - 0.5) * scale + 0.5
    mapped_y = (hand_cursor.y - 0.5) * scale + 0.5

    mapped_x = max(0.0, min(1.0, mapped_x))
    mapped_y = max(0.0, min(1.0, mapped_y))

    screen_x = int(mapped_x * (SCREEN_WIDTH - 4)) + 2
    screen_y = int(mapped_y * (SCREEN_HEIGHT - 4)) + 2

    pyautogui.moveTo(screen_x, screen_y)


def drag_click_mouse(hand_landmarks, mouse_is_down):
    pinching = is_pinching(hand_landmarks)

    if pinching and not mouse_is_down:
        pyautogui.mouseDown(button="left")
        return True

    if not pinching and mouse_is_down:
        pyautogui.mouseUp(button="left")
        return False

    return mouse_is_down


if __name__ == "__main__":
    main()
