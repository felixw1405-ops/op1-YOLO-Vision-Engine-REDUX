from dataclasses import dataclass
import threading
import time
import numpy as np


class AtomicReference:
    """
    Thread-safe holder for the latest object.
    Latest-wins semantics.
    """

    def __init__(self):
        self._value = None
        self._lock = threading.Lock()

    def set(self, value):
        with self._lock:
            self._value = value

    def get(self):
        with self._lock:
            return self._value


@dataclass(frozen=True)
class FramePacket:
    """
    Published by ScreenCapture.
    """

    frame_id: int

    capture_timestamp: float

    frame: np.ndarray


@dataclass(frozen=True)
class TrackPacket:
    """
    Published by DetectorWorker.
    """

    frame_id: int

    capture_timestamp: float

    detection_timestamp: float

    detect_ms: float

    tracks: tuple


class FPSCounter:

    def __init__(self):

        self.last = time.perf_counter()

        self.fps = 0.0

    def tick(self):

        now = time.perf_counter()

        delta = now - self.last

        if delta > 0:
            self.fps = 1.0 / delta

        self.last = now

        return self.fps
