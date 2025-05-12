import pyautogui
import cv2 as cv

class ScrollController:
    def __init__(self, scroll_amount=50, threshold=10):
        self.prev_wrist_x = None
        self.prev_wrist_y = None
        self.scroll_amount = scroll_amount  # Constant scroll amount
        self.threshold = threshold  # Threshold to prevent jitter

    def reset(self):
        """Reset wrist position tracking."""
        self.prev_wrist_x = None
        self.prev_wrist_y = None

    def scroll(self, debug_image, wrist_coords):
        """Handle constant scroll based on wrist movement direction."""
        current_x, current_y = wrist_coords

        # Ensure there is a previous wrist position to compare with
        if self.prev_wrist_x is not None and self.prev_wrist_y is not None:
            dx = current_x - self.prev_wrist_x
            dy = current_y - self.prev_wrist_y

            # If vertical movement is significant (bigger than horizontal), scroll vertically
            if abs(dy) > abs(dx) and abs(dy) > self.threshold:
                # Scroll down if dy > 0, up if dy < 0
                pyautogui.scroll(-self.scroll_amount if dy > 0 else self.scroll_amount)
                direction = 'Down' if dy > 0 else 'Up'
                cv.putText(debug_image, f"Scroll {direction}", (10, 150),
                           cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # If horizontal movement is significant, scroll horizontally
            elif abs(dx) > self.threshold:
                # Scroll right if dx > 0, left if dx < 0
                pyautogui.hscroll(self.scroll_amount if dx > 0 else -self.scroll_amount)
                direction = 'Right' if dx > 0 else 'Left'
                cv.putText(debug_image, f"Scroll {direction}", (10, 150),
                           cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Update previous wrist position for the next iteration
        self.prev_wrist_x = current_x
        self.prev_wrist_y = current_y

