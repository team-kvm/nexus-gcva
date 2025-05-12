import screen_brightness_control as sbc

class BrightnessController:
    def __init__(self, step=5):
        self.step = step

    def increase(self):
        try:
            current = sbc.get_brightness(display=0)[0]
            sbc.set_brightness(min(100, current + self.step))
        except Exception as e:
            print("Brightness increase failed:", e)

    def decrease(self):
        try:
            current = sbc.get_brightness(display=0)[0]
            sbc.set_brightness(max(0, current - self.step))
        except Exception as e:
            print("Brightness decrease failed:", e)

    def get_brightness_percent(self):
        try:
            return sbc.get_brightness(display=0)[0]
        except Exception:
            return -1

