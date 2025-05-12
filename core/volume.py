from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

class VolumeController:
    def __init__(self, step=0.02):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
        self.step = step

    def increase(self):
        current = self.volume_ctrl.GetMasterVolumeLevelScalar()
        self.volume_ctrl.SetMasterVolumeLevelScalar(min(1.0, current + self.step), None)

    def decrease(self):
        current = self.volume_ctrl.GetMasterVolumeLevelScalar()
        self.volume_ctrl.SetMasterVolumeLevelScalar(max(0.0, current - self.step), None)

    def get_volume_percent(self):
        return int(self.volume_ctrl.GetMasterVolumeLevelScalar() * 100)

