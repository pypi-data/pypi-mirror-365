import os

LOCATE_AND_CLICK_DELAY = float(os.getenv("PYAUTOGUIDE_LOCATE_AND_CLICK_DELAY", 0.3))

# pixels per second, used for calculating move duration
POINTER_SPEED = int(os.getenv("PYAUTOGUIDE_POINTER_SPEED", 1000))
