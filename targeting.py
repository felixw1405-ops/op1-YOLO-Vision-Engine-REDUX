import math
import time


class Targeter:
    """Locks one track until it leaves the keep-radius, then re-picks nearest."""

    def __init__(self, cfg):
        self.cfg = cfg
        self._locked = None
        self._last = None

    def reset(self):
        self._locked = None
        self._last = None

    def _predict(self, ex, ey):
        if not self.cfg.PREDICT:
            return ex, ey
        now = time.perf_counter()
        if self._last is not None:
            lx, ly, lt = self._last
            dt = now - lt
            if 0.0 < dt < 0.25:
                lead = self.cfg.PREDICTION_MS / 1000.0
                ex += (ex - lx) / dt * lead
                ey += (ey - ly) / dt * lead
        self._last = (ex, ey, now)
        return ex, ey

    def select(self, track_packet, geom, frame_shape, ref):
        if track_packet is None:
            return None

        scale = geom.scale(frame_shape)
        lock_dist = geom.monitor["height"] * self.cfg.MAX_LOCK_DIST
        keep_dist = lock_dist * self.cfg.HYSTERESIS

        cands = []
        for t in track_packet.tracks:
            if t["missing"] > 0:
                continue
            cx, cy = geom.box_aim_point(t["box"], scale, self.cfg.AIM_Y_FRACTION)
            ex, ey = cx - ref[0], cy - ref[1]
            cands.append((t.get("id", t.get("track_id")), ex, ey, math.hypot(ex, ey)))

        if not cands:
            self._locked = None
            return None

        if self._locked is not None:
            for tid, ex, ey, d in cands:
                if tid == self._locked and d <= keep_dist:
                    return self._predict(ex, ey)

        best = None
        for c in cands:
            if c[3] <= lock_dist and (best is None or c[3] < best[3]):
                best = c
        if best is None:
            self._locked = None
            return None

        self._locked = best[0]
        self._last = None
        return self._predict(best[1], best[2])
