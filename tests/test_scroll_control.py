import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "main"))

from scroll_control import ScrollControl, select_hands, pinch_ratio


def hand(y=0.5, gesture=True):
    points = [SimpleNamespace(x=0.5, y=y) for _ in range(21)]
    for base, joint, tip, x in ((5, 6, 8, 0.4), (9, 10, 12, 0.45),
                               (13, 14, 16, 0.55), (17, 18, 20, 0.6)):
        points[base] = SimpleNamespace(x=x, y=y)
        points[joint] = SimpleNamespace(x=x, y=y - 0.05)
        raised = gesture and base in (5, 9)
        points[tip] = SimpleNamespace(x=x, y=y - (0.15 if raised else 0.02))
    points[4] = SimpleNamespace(x=0.41 if gesture else 0.65,
                                y=y - 0.15 if gesture else y + 0.1)
    return points


class ScrollTests(unittest.TestCase):
    def arm(self):
        control = ScrollControl()
        self.assertEqual(control.update(hand(), 0), 0)
        self.assertTrue(control.active)
        return control

    def test_engages_immediately_without_initial_scroll(self):
        control = self.arm()
        self.assertLess(pinch_ratio(hand()), 0.4)
        self.assertGreater(pinch_ratio(hand(gesture=False)), 0.65)
        self.assertLess(control.update(hand(0.45), 0.02), 0)

    def test_direct_direction_dead_zone_and_stop(self):
        control = self.arm()
        self.assertEqual(control.update(hand(0.499), 0.02), 0)
        self.assertLess(control.update(hand(0.45), 0.04), 0)
        self.assertEqual(control.update(hand(0.45), 0.06), 0)
        self.assertGreater(control.update(hand(0.50), 0.08), 0)

    def test_larger_swipe_produces_more_scroll(self):
        small, large = self.arm(), self.arm()
        self.assertGreater(abs(large.update(hand(0.40), 0.02)),
                           abs(small.update(hand(0.47), 0.02)))

    def test_pinch_shape_changes_do_not_scroll_without_palm_motion(self):
        control = self.arm()
        points = hand()
        points[4].y -= 0.03
        points[8].y -= 0.03
        self.assertEqual(control.update(points, 0.02), 0)

    def test_hysteresis_prevents_chattering(self):
        control = self.arm()
        points = hand()
        points[4].x = points[8].x + 0.11  # Ratio 0.55: hold, but do not engage.
        self.assertEqual(control.update(points, 0.02), 0)
        self.assertTrue(control.active)
        control.reset()
        self.assertEqual(control.update(points, 0.04), 0)
        self.assertFalse(control.active)

    def test_other_fingers_do_not_need_a_specific_pose(self):
        control = ScrollControl()
        points = hand()
        for tip in (12, 16, 20):
            points[tip].y -= 0.2
        self.assertEqual(control.update(points, 0), 0)
        self.assertTrue(control.active)

    def test_sub_step_movement_accumulates_across_frames(self):
        control = self.arm()
        outputs = [control.update(hand(0.5 - index * 0.006), index * 0.02)
                   for index in range(1, 11)]
        self.assertLess(sum(outputs), 0)

    def test_same_swipe_at_different_frame_rates(self):
        totals = []
        for frames in (10, 40):
            control = self.arm()
            totals.append(sum(control.update(hand(0.5 - i * 0.10 / frames),
                                             i * 0.2 / frames)
                              for i in range(1, frames + 1)))
        self.assertLessEqual(abs(totals[0] - totals[1]), 1)

    def test_jitter_does_not_scroll(self):
        control = self.arm()
        outputs = [control.update(hand(0.5 + (-1) ** i * 0.002), i * 0.02)
                   for i in range(1, 31)]
        self.assertEqual(sum(abs(step) for step in outputs), 0)

    def test_large_output_is_bounded_without_queued_scroll(self):
        control = self.arm()
        self.assertEqual(control.update(hand(0.30), 0.02), -8)
        self.assertEqual(control.update(hand(0.30), 0.04), 0)

    def test_tracking_gap_and_landmark_jump_do_not_scroll(self):
        control = self.arm()
        self.assertEqual(control.update(hand(0.10), 0.02), 0)
        self.assertEqual(control.update(hand(0.50), 1), 0)
        self.assertEqual(control.update(hand(0.50), 1.02), 0)

    def test_reset_on_loss_disable_or_release(self):
        for landmarks, enabled in ((None, True), (hand(), False),
                                   (hand(gesture=False), True)):
            with self.subTest(enabled=enabled):
                control = self.arm()
                self.assertEqual(control.update(landmarks, 0.02, enabled), 0)
                self.assertFalse(control.active)
                self.assertEqual(control.update(hand(0.3), 0.04), 0)
                self.assertTrue(control.active)

    def test_hand_roles_do_not_depend_on_detection_order(self):
        left, right = hand(), hand(0.6)
        def category(name):
            return [SimpleNamespace(category_name=name, score=0.95)]
        for points, labels in (([left, right], ["Right", "Left"]),
                               ([right, left], ["Left", "Right"])):
            result = SimpleNamespace(hand_landmarks=points,
                                     handedness=[category(label) for label in labels])
            selected = select_hands(result)
            self.assertIs(selected["Left"], left)
            self.assertIs(selected["Right"], right)

    def test_calibration_can_reverse_default_hand_assignment(self):
        left = hand()
        result = SimpleNamespace(hand_landmarks=[left], handedness=[[
            SimpleNamespace(category_name="Left", score=0.95)
        ]])
        self.assertIs(select_hands(result, left_label="Left")["Left"], left)

    def test_uncertain_hand_is_ignored(self):
        result = SimpleNamespace(hand_landmarks=[hand()], handedness=[[
            SimpleNamespace(category_name="Left", score=0.6)
        ]])
        self.assertEqual(select_hands(result), {})


if __name__ == "__main__":
    unittest.main()
