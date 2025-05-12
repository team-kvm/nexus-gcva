import csv
import cv2
import time
import pyautogui
from model import KeyPointClassifier
from utils import (
    draw_info,
    draw_info_text,
    draw_landmarks,
    draw_bounding_rect,
    calc_landmark_list,
    calc_bounding_rect,
    pre_process_landmark,
)
from core import MouseController, VolumeController, BrightnessController, ScrollController

class GestureController:
    def __init__(self, args):
        self.sensitivity = args.sensitivity
        self.click_cooldown = args.click_cooldown
        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse = MouseController(self.sensitivity, self.click_cooldown)
        self.keypoint_classifier = KeyPointClassifier()

        self.volume = VolumeController()
        self.brightness = BrightnessController()
        self.scroll_ctrl = ScrollController()
        self.super_prev_x = None
        self.super_prev_y = None
        self.super_threshold = 10

        with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
            self.labels = [row[0] for row in csv.reader(f)]

        self.prev_index_dipped = False
        self.prev_middle_dipped = False
        self.prev_finger_x = None
        self.prev_finger_y = None
        self.mode = 0
        self.number = -1

    def increase_sensitivity(self):
        self.sensitivity += 0.1
        self.mouse.set_sensitivity(self.sensitivity)
        print(f"Sensitivity increased to: {self.sensitivity:.1f}")

    def decrease_sensitivity(self):
        self.sensitivity = max(0.1, self.sensitivity - 0.1)
        self.mouse.set_sensitivity(self.sensitivity)
        print(f"Sensitivity decreased to: {self.sensitivity:.1f}")

    def handle_super_mode_right(self, image, wrist):
        current_x, current_y = wrist
        if self.super_prev_x is not None and self.super_prev_y is not None:
            dx = current_x - self.super_prev_x
            dy = current_y - self.super_prev_y

            if abs(dy) > abs(dx) and abs(dy) > self.super_threshold:
                if dy < 0:
                    self.volume.increase()
                else:
                    self.volume.decrease()
            elif abs(dx) > self.super_threshold:
                if dx > 0:
                    self.brightness.increase()
                else:
                    self.brightness.decrease()

        self.super_prev_x = current_x
        self.super_prev_y = current_y

    def process_hand(self, image, results):
        if results.multi_hand_landmarks is None:
            self.prev_finger_x = None
            self.prev_finger_y = None
            return image

        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            brect = calc_bounding_rect(image, hand_landmarks)
            landmark_list = calc_landmark_list(image, hand_landmarks)
            pre_processed_landmarks = pre_process_landmark(landmark_list)

            hand_sign_id = self.keypoint_classifier(pre_processed_landmarks)
            label = self.labels[hand_sign_id]

            index_tip = landmark_list[8]
            index_pip = landmark_list[6]
            middle_tip = landmark_list[12]
            middle_pip = landmark_list[10]

            index_dipped = index_tip[1] > index_pip[1]
            middle_dipped = middle_tip[1] > middle_pip[1]

            if label == 'Gun':
                image = self.mouse.move_cursor(index_tip, self.prev_finger_x, self.prev_finger_y, image)
                self.prev_finger_x, self.prev_finger_y = index_tip[0], index_tip[1]
            elif label == 'Cursor':
                now = time.time()
                if index_dipped and not self.prev_index_dipped:
                    if self.mouse.click_left(now):
                        cv2.putText(image, "Left Click", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                if middle_dipped and not self.prev_middle_dipped:
                    if self.mouse.click_right(now):
                        cv2.putText(image, "Right Click", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(image, "Click Control Active", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            elif label == 'Super':
                if handedness.classification[0].label == "Right":
                    self.handle_super_mode_right(image, landmark_list[0])
                    cv2.putText(image, f"Brightness: {self.brightness.get_brightness_percent()}%", (10, 180),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    cv2.putText(image, f"Volume: {self.volume.get_volume_percent()}%", (10, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    self.scroll_ctrl.reset()
                else:
                    self.scroll_ctrl.scroll(image, landmark_list[0])

            self.prev_index_dipped = index_dipped
            self.prev_middle_dipped = middle_dipped

            image = draw_bounding_rect(True, image, brect)
            image = draw_landmarks(image, landmark_list)
            image = draw_info_text(image, brect, handedness, label)

        return image

    def draw_info(self, image, fps):
        return draw_info(image, fps, self.mode, self.number, self.sensitivity)
