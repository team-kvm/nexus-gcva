import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

with mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5,
                    min_tracking_confidence=0.5, max_num_hands=1) as hands:
    while cap.isOpened():
        # Read frame from webcam
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # Flip the image horizontally for a more intuitive mirror view
        image = cv2.flip(image, 1)
        
        # To improve performance, optionally mark the image as not writeable
        image.flags.writeable = False
        
        # Convert the image to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        results = hands.process(image_rgb)
        
        # Draw hand landmarks on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Print information about detected hands
        hand_landmarks_list = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks and connections
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Store landmark positions
                hand_landmarks_list.append(hand_landmarks)
                
                # Get index finger tip coordinates (landmark 8)
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                h, w, c = image.shape
                index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Draw a circle at the index finger tip
                cv2.circle(image, (index_x, index_y), 10, (0, 0, 0), -1)
                
                # Display coordinates
                cv2.putText(image, f"({index_x}, {index_y})", (index_x + 15, index_y + 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Display the number of hands detected
        cv2.putText(image, f"Hands detected: {len(hand_landmarks_list)}", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Display the image
        cv2.imshow('MediaPipe Hand Tracking', image)
        
        # Press 'q' to exit
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
