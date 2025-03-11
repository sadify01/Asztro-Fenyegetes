import ctypes
from screeninfo import get_monitors

for monitor in get_monitors():
    monitor_width = monitor.width
    monitor_height = monitor.height

user32 = ctypes.windll.user32
dc = user32.GetDC(0)
refresh_rate = ctypes.windll.gdi32.GetDeviceCaps(dc, 116)

dt = 100 / refresh_rate
spaceship_size = monitor_width * 0.05
base_speed = 100 * monitor_width / 750
unit = monitor_width * 0.05
