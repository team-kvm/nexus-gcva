import pyautogui

class MouseController:
    def __init__(self, sensitivity=3, cooldown=0.5):
        self.sensitivity = sensitivity
        self.cooldown = cooldown
        self.last_left_click = 0
        self.last_right_click = 0
        self.last_double_click = 0
        self.screen_width, self.screen_height = pyautogui.size()

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity

    def move_cursor(self, current_finger, prev_x, prev_y, image):
        if prev_x is not None and prev_y is not None:
            delta_x = (current_finger[0] - prev_x) * self.sensitivity
            delta_y = (current_finger[1] - prev_y) * self.sensitivity
            x, y = pyautogui.position()
            new_x = max(0, min(x + delta_x, self.screen_width))
            new_y = max(0, min(y + delta_y, self.screen_height))
            pyautogui.moveTo(new_x, new_y)
            import cv2
            cv2.putText(image, "Movement Active", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return image

    def click_left(self, current_time):
        if current_time - self.last_left_click > self.cooldown:
            pyautogui.click()
            self.last_left_click = current_time
            return True
        return False

    def click_right(self, current_time):
        if current_time - self.last_right_click > self.cooldown:
            pyautogui.rightClick()
            self.last_right_click = current_time
            return True
        return False

    def double_click(self, current_time):
        if current_time - self.last_double_click > self.cooldown:
            pyautogui.doubleClick()
            self.last_double_click = current_time
            return True
        return False
