# ---------------- AIM TUNING ----------------
NUDGE_STRENGTH = 0.9   # fraction of error per frame; 1.0 = snap in one frame
NUDGE_DEADZONE = 1     # px; stop within this of the target
NUDGE_MAX_STEP = 300   # px per frame cap (raise so far targets aren't throttled)
NUDGE_SMOOTHING = 0.3  # 0 = off; 0.3-0.6 low-passes the error to kill jitter
# -------------------------------------------


class Nudger:
    def __init__(self):
        self.strength = NUDGE_STRENGTH
        self.deadzone = NUDGE_DEADZONE
        self.max_step = NUDGE_MAX_STEP
        self.smoothing = NUDGE_SMOOTHING
        self._ex = 0.0
        self._ey = 0.0
        self._rx = 0.0   # fractional remainder carried between frames
        self._ry = 0.0

    def reset(self):
        self._ex = self._ey = self._rx = self._ry = 0.0

    def update(self, target_x, target_y, ref_x, ref_y):
        ex = target_x - ref_x
        ey = target_y - ref_y

        if self.smoothing > 0:
            self._ex += (ex - self._ex) * self.smoothing
            self._ey += (ey - self._ey) * self.smoothing
            ex, ey = self._ex, self._ey

        if abs(ex) < self.deadzone:
            ex = 0.0
        if abs(ey) < self.deadzone:
            ey = 0.0

        mx = max(-self.max_step, min(self.max_step, ex * self.strength)) + self._rx
        my = max(-self.max_step, min(self.max_step, ey * self.strength)) + self._ry

        ix, iy = round(mx), round(my)
        self._rx, self._ry = mx - ix, my - iy
        return ix, iy
