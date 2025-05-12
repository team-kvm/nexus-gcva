import argparse
import copy
import cv2 as cv
from utils import setup_camera
from hands import HandDetector
from gesture_controller import GestureController
from utils import FpsCalculator

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=1)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence", type=float, default=0.7)
    parser.add_argument("--min_tracking_confidence", type=float, default=0.5)
    parser.add_argument("--sensitivity", type=float, default=3)
    parser.add_argument("--click_cooldown", type=float, default=0.5)
    return parser.parse_args()

def main():
    args = get_args()
    cap = setup_camera(args.device, args.width, args.height)
    detector = HandDetector(args)
    controller = GestureController(args)
    fps_calc = FpsCalculator(buffer_len=10)

    while True:
        key = cv.waitKey(10)
        if key == 27:
            break
        if key in [43, 61]:
            controller.increase_sensitivity()
        if key == 45:
            controller.decrease_sensitivity()

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv.flip(frame, 1)
        debug_image = copy.deepcopy(frame)
        results = detector.detect(frame)

        debug_image = controller.process_hand(debug_image, results)

        fps = fps_calc.get()
        debug_image = controller.draw_info(debug_image, fps)

        cv.imshow('Hand Gesture Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
