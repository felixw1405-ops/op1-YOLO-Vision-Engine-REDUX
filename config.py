"""Every tunable in one place. Import as `import config as cfg`."""

# ---------------- monitor / capture region ----------------
MONITOR = 1
ROI_W = 0.85            # centred rectangle, fraction of the monitor
ROI_H = 0.75            # bigger = sees more, costs more capture time
CROP_CENTERED = True    # False if your capture anchors the crop top-left

# ---------------- loop rates ----------------
AIM_HZ = 240
RENDER_HZ = 120

# ---------------- preview ----------------
PREVIEW_ENABLED = True
PREVIEW_WIDTH = 1280    # window is resizable; drag it to size
DRAW_BOXES = True
WINDOW_TITLE = "YOLO Vision Engine v6"

# ---------------- aim ----------------
AIM_MODE = "relative"   # "relative" (pointer-lock 3D) | "cursor" (absolute/2D)
GAIN = 0.6              # relative only: mouse px per screen px -> calibrate (F9)
STRENGTH = 0.5          # cursor only: fraction of error per frame
DEADZONE = 8.0          # screen px; ~= 0.5 / GAIN when GAIN is small
MAX_STEP = 400          # mouse px per step
SMOOTHING = 0.0         # 0..1 low-pass on error
LOOP_COMP = 0.9         # relative only: in-flight command credit

# ---------------- target selection ----------------
AIM_Y_FRACTION = 0.5    # 0.5 = box centre, 0.3 = head
MAX_LOCK_DIST = 0.40    # acquire within this fraction of screen height
HYSTERESIS = 1.6        # hold lock out to this * the radius
PREDICT = False
PREDICTION_MS = 25.0

# ---------------- keys ----------------
KEY_TOGGLE = "f8"
KEY_CALIBRATE = "f9"
KEY_GAIN_DOWN = "f10"
KEY_GAIN_UP = "f11"
CALIBRATE_DELTA = 50.0  # small test move; raise only if GAIN comes out < 0.05

# ---------------- debug ----------------
DEBUG = False
LOG_HZ = 1.0
