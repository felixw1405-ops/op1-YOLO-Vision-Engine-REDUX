"""Single authority for screen <-> frame coordinate maths."""


class Geometry:
    def __init__(self, monitor, roi_w, roi_h, crop_centered=True):
        self.monitor = monitor
        self.roi_w = roi_w
        self.roi_h = roi_h

        if crop_centered:
            self.left = monitor["left"] + monitor["width"] * (1.0 - roi_w) / 2.0
            self.top = monitor["top"] + monitor["height"] * (1.0 - roi_h) / 2.0
        else:
            self.left = monitor["left"]
            self.top = monitor["top"]

        self.region_w = monitor["width"] * roi_w
        self.region_h = monitor["height"] * roi_h
        self.centre = (
            monitor["left"] + monitor["width"] / 2.0,
            monitor["top"] + monitor["height"] / 2.0,
        )

    def scale(self, frame_shape):
        return frame_shape[1] / self.region_w

    def frame_to_screen(self, x, y, scale):
        return self.left + x / scale, self.top + y / scale

    def box_aim_point(self, box, scale, y_frac):
        x1, y1, x2, y2 = box
        sx = self.left + (x1 + x2) * 0.5 / scale
        sy = self.top + (y1 + (y2 - y1) * y_frac) / scale
        return sx, sy
