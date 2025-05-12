#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import argparse
import time

import cv2 as cv
import mediapipe as mp
import pyautogui

from utils import (
    FpsCalculator,
    draw_info,
    draw_info_text,
    draw_landmarks,
    draw_bounding_rect,
    calc_landmark_list,
    calc_bounding_rect,
    pre_process_landmark
)

from model import KeyPointClassifier

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)
    parser.add_argument("--sensitivity",
                        help='mouse movement sensitivity',
                        type=float,
                        default=3)
    parser.add_argument("--click_cooldown",
                        help='minimum time between clicks in seconds',
                        type=float,
                        default=0.5)

    args = parser.parse_args()

    return args

def main():
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    use_brect = True

    # Camera preparation
    # cap = cv.VideoCapture(cap_device)
    cap = cv.VideoCapture(1, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # Load model
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    keypoint_classifier = KeyPointClassifier()

    # Read labels
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]

    # Calculate FPS
    cvFpsCalc = FpsCalculator(buffer_len=10)

    # Get screen resolution for mouse movement
    screen_width, screen_height = pyautogui.size()
    
    # Variables for cursor control
    # Previous finger position
    prev_finger_x, prev_finger_y = None, None
    # Get initial sensitivity from command line args
    sensitivity = args.sensitivity   
    # For smoothing mouse movement (Lower values = more smoothing)
    smoothing = 0.3
    
    # For click tracking
    last_left_click_time = 0
    last_right_click_time = 0
    click_cooldown = args.click_cooldown
    
    # Track finger state for gesture recognition
    index_finger_dipped = False
    middle_finger_dipped = False
    prev_index_finger_dipped = False
    prev_middle_finger_dipped = False

    mode = 0

    while True:
        fps = cvFpsCalc.get()

        # Process Key (ESC: end)
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break
        # Adjust sensitivity with + and - keys
        if key == 43 or key == 61:
            sensitivity += 0.1
            print(f"Sensitivity increased to: {sensitivity:.1f}")
        if key == 45:
            sensitivity = max(0.1, sensitivity - 0.1)
            print(f"Sensitivity decreased to: {sensitivity:.1f}")
            
        number, mode = select_mode(key, mode)

        # Camera capture
        ret, image = cap.read()
        if not ret:
            break
        # Mirror display
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                # Bounding box calculation
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)
                
                # Write to the dataset file
                logging_csv(number, mode, pre_processed_landmark_list)

                # Hand sign classification
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                
                # Get the label for the current hand sign
                hand_sign_label = keypoint_classifier_labels[hand_sign_id]

                # Index finger and middle finger positions (needed for both gestures)
                index_finger_tip = landmark_list[8]
                # PIP joint of index finger
                index_finger_pip = landmark_list[6]
                middle_finger_tip = landmark_list[12]
                # PIP joint of middle finger
                middle_finger_pip = landmark_list[10]

                current_finger_x, current_finger_y = index_finger_tip[0], index_finger_tip[1]

                # Detect if index finger is dipped (tip below PIP joint)
                index_finger_dipped = index_finger_tip[1] > index_finger_pip[1]

                # Detect if middle finger is dipped (tip below PIP joint)
                middle_finger_dipped = middle_finger_tip[1] > middle_finger_pip[1]

                # Move mouse cursor if the detected hand sign is 'Gun'
                if hand_sign_label == 'Gun':
                    if prev_finger_x is not None and prev_finger_y is not None:
                        # Calculate the movement delta (how much the finger moved)
                        delta_x = (current_finger_x - prev_finger_x) * sensitivity
                        delta_y = (current_finger_y - prev_finger_y) * sensitivity
                        
                        # Get current mouse position
                        current_mouse_x, current_mouse_y = pyautogui.position()
                        
                        # Calculate new mouse position based on the delta movement
                        new_mouse_x = current_mouse_x + delta_x
                        new_mouse_y = current_mouse_y + delta_y
                        
                        # Keep cursor within screen bounds
                        new_mouse_x = max(0, min(new_mouse_x, screen_width))
                        new_mouse_y = max(0, min(new_mouse_y, screen_height))
                        
                        # Move the mouse cursor
                        pyautogui.moveTo(new_mouse_x, new_mouse_y)
                        
                        # Visual feedback that cursor control is active
                        cv.putText(debug_image, f"Movement Active", 
                                  (10, 120), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)
                    
                    # Update previous finger position
                    prev_finger_x, prev_finger_y = current_finger_x, current_finger_y

                # Handle clicks if the detected hand sign is 'Cursor'
                elif hand_sign_label == 'Cursor':
                    current_time = time.time()
                    
                    # Left click when index finger is dipped
                    if index_finger_dipped and not prev_index_finger_dipped:
                        if current_time - last_left_click_time > click_cooldown:
                            pyautogui.click()  # Left click
                            last_left_click_time = current_time
                            cv.putText(debug_image, "Left Click", (10, 150), 
                                      cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv.LINE_AA)
                    
                    # Right click when middle finger is dipped
                    if middle_finger_dipped and not prev_middle_finger_dipped:
                        if current_time - last_right_click_time > click_cooldown:
                            pyautogui.rightClick()  # Right click
                            last_right_click_time = current_time
                            cv.putText(debug_image, "Right Click", (10, 180), 
                                      cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv.LINE_AA)
                    
                    # Visual feedback that click control is active
                    cv.putText(debug_image, f"Click Control Active", 
                              (10, 120), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)
                else:
                    # Reset previous position and finger states if hand sign changes
                    prev_finger_x, prev_finger_y = None, None

                # Always update previous finger dip states (needed for both gestures)
                prev_index_finger_dipped = index_finger_dipped
                prev_middle_finger_dipped = middle_finger_dipped

                # Drawing part
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    handedness,
                    keypoint_classifier_labels[hand_sign_id],
                )
                debug_image = draw_info(debug_image, fps, mode, number, sensitivity)

        # Screen reflection #############################################################
        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    return number, mode

def logging_csv(number, mode, landmark_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    return

if __name__ == '__main__':
    main()
