import mediapipe as mp
import cv2

class HandDetector:
    def __init__(self, args):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=args.use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=args.min_detection_confidence,
            min_tracking_confidence=args.min_tracking_confidence
        )

    def detect(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True
        return results
