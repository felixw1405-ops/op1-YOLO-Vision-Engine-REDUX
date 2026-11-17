import time

from Quartz.CoreGraphics import (
    CGEventCreate,
    CGEventCreateMouseEvent,
    CGEventGetLocation,
    CGEventPost,
    CGEventSetIntegerValueField,
    CGWarpMouseCursorPosition,
    kCGEventMouseMoved,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
    kCGMouseEventDeltaX,
    kCGMouseEventDeltaY,
)


class Aim:
    """One controller, two modes: relative (deltas) | cursor (absolute)."""

    def __init__(self, cfg, geom):
        self.cfg = cfg
        self.geom = geom
        self.gain = cfg.GAIN
        self.strength = cfg.STRENGTH
        self.deadzone = cfg.DEADZONE
        self.max_step = cfg.MAX_STEP
        self.smoothing = cfg.SMOOTHING
        self.loop_comp = cfg.LOOP_COMP
        self._ex = self._ey = 0.0
        self._rx = self._ry = 0.0
        self._pending = []
        self._vcursor = [geom.centre[0], geom.centre[1]]
        self._calib = {"phase": 0, "e0": None, "t": 0.0}

    def reset(self):
        self._ex = self._ey = self._rx = self._ry = 0.0
        self._pending.clear()
        self._vcursor[0], self._vcursor[1] = self.geom.centre

    def warp(self):
        CGWarpMouseCursorPosition(self.geom.centre)
        self._vcursor[0], self._vcursor[1] = self.geom.centre

    @property
    def calibrating(self):
        return self._calib["phase"] != 0

    def ref(self):
        if self.cfg.AIM_MODE == "relative":
            return self.geom.centre
        p = CGEventGetLocation(CGEventCreate(None))
        return p.x, p.y

    def _post_rel(self, dx, dy):
        self._vcursor[0] += dx
        self._vcursor[1] += dy
        e = CGEventCreateMouseEvent(
            None, kCGEventMouseMoved,
            (self._vcursor[0], self._vcursor[1]), kCGMouseButtonLeft,
        )
        CGEventSetIntegerValueField(e, kCGMouseEventDeltaX, int(dx))
        CGEventSetIntegerValueField(e, kCGMouseEventDeltaY, int(dy))
        CGEventPost(kCGHIDEventTap, e)

    def _post_abs(self, x, y):
        e = CGEventCreateMouseEvent(None, kCGEventMouseMoved, (x, y), kCGMouseButtonLeft)
        CGEventPost(kCGHIDEventTap, e)

    def _command(self, ex, ey, frame_t):
        if self.cfg.AIM_MODE == "relative":
            now = time.perf_counter()
            self._pending = [
                p for p in self._pending
                if (now - p[0]) < 0.15 and (frame_t is None or p[0] > frame_t)
            ]
            px = sum(p[1] for p in self._pending)
            py = sum(p[2] for p in self._pending)
            ex -= (px / self.gain) * self.loop_comp
            ey -= (py / self.gain) * self.loop_comp
            scale = self.gain
        else:
            scale = self.strength

        if self.smoothing > 0:
            self._ex += (ex - self._ex) * self.smoothing
            self._ey += (ey - self._ey) * self.smoothing
            ex, ey = self._ex, self._ey

        if abs(ex) < self.deadzone:
            ex = 0.0
        if abs(ey) < self.deadzone:
            ey = 0.0

        mx = max(-self.max_step, min(self.max_step, ex * scale)) + self._rx
        my = max(-self.max_step, min(self.max_step, ey * scale)) + self._ry
        ix, iy = round(mx), round(my)
        self._rx, self._ry = mx - ix, my - iy
        return ix, iy

    def step(self, ex, ey, frame_t):
        mx, my = self._command(ex, ey, frame_t)
        if not (mx or my):
            return
        if self.cfg.AIM_MODE == "relative":
            self._post_rel(mx, my)
            self._pending.append((time.perf_counter(), mx, my))
        else:
            rx, ry = self.ref()
            self._post_abs(rx + mx, ry + my)

    def request_calibration(self):
        if self._calib["phase"] == 0:
            self._calib["phase"] = 1

    def calibrate(self, ex):
        ph = self._calib["phase"]
        if ph == 1:
            self._calib["e0"] = ex
            self._calib["t"] = time.perf_counter()
            self._post_rel(int(self.cfg.CALIBRATE_DELTA), 0)
            self._pending.clear()
            self._calib["phase"] = 2
        elif ph == 2:
            if time.perf_counter() - self._calib["t"] > 0.4:
                print("[calib] timed out (lost lock?)")
                self._calib["phase"] = 0
                return
            denom = self._calib["e0"] - ex
            if abs(denom) > 1.0:
                self.gain = max(0.005, min(20.0, self.cfg.CALIBRATE_DELTA / denom))
                print(f"[calib] denom={denom:.0f}  GAIN = {self.gain:.4f}")
            else:
                print("[calib] target barely moved - retry on a still target")
            self._calib["phase"] = 0
