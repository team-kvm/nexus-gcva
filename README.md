# Nexus GCVA - Gesture Controller & Voice Assistant

### Installation

```bash
git clone https://github.com/team-kvm/nexus-gcva.git
cd nexus-gcva
pip install -r requirements.txt
```

## How It Works

### Gesture Recognition

- **Webcam Input** is captured using **OpenCV**.
- **Mediapipe** is used to extract hand **landmarks** from each video frame.
- Landmarks are processed using a **custom-trained keypoint classifier**.
- The classifier is trained on CSV logs of keypoints collected during logging mode.

### Logging Mode

- Activate logging mode by pressing the `K` key.
- Use number keys (`0`–`9`) to label and log gesture data for training.
- Logged data is stored as CSV for model training and future classification.

### Mapped Gestures & Actions

| Gesture                          | Action                                         |
|----------------------------------|------------------------------------------------|
| **Open Thumb + Peace** (Gun)     | Cursor movement                                |
| **Peace**                        | Mouse click                                    |
| **Super (Left Hand)**            | Scroll up/down, left/right                     |
| **Super (Right Hand)**           | Brightness (horizontal), Volume (vertical)     |
| **Closed Fist**                  | Record audio and send to voice assistant       |
| **Open Palm**                    | Reset state / flag for next recording          |

---

## Voice Assistant

The built-in voice assistant is a lightweight command parser that responds to simple voice commands. It supports:

- Web Search
- Map Search
- Basic system tasks and utilities

### Voice Input Triggers
- Activated when **Closed Fist** gesture is detected.
- Audio is recorded and parsed for intent.
- Use **Open Palm** to reset and allow new recordings.
