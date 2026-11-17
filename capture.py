import threading
import time

import cv2
import numpy as np
from mss import MSS

from shared import AtomicReference, FramePacket, FPSCounter


class ScreenCapture:

    def __init__(
        self,
        monitor=1,
        search_width=1.0,
        search_height=1.0,
    ):

        self.sct = MSS()

        full = self.sct.monitors[monitor]

        width = int(full["width"] * search_width)
        height = int(full["height"] * search_height)

        self.monitor = {
            "left": full["left"] + (full["width"] - width) // 2,
            "top": full["top"] + (full["height"] - height) // 2,
            "width": width,
            "height": height,
        }

        # Latest published frame
        self.latest = AtomicReference()

        self.running = False
        self.thread = None

        self.frame_id = 0

        self.capture_ms = 0.0

        self.fps_counter = FPSCounter()
        self.capture_fps = 0.0

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join()

    def _capture_loop(self):

        while self.running:

            start = time.perf_counter()

            screenshot = self.sct.grab(self.monitor)

            frame = np.asarray(screenshot)

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGRA2BGR
            )

            # Published frames are read-only
            frame.setflags(write=False)

            self.frame_id += 1

            packet = FramePacket(
                frame_id=self.frame_id,
                capture_timestamp=time.perf_counter(),
                frame=frame
            )

            self.latest.set(packet)

            end = time.perf_counter()

            self.capture_ms = (end - start) * 1000.0

            self.capture_fps = self.fps_counter.tick()

    def get_latest(self):
        return self.latest.get()

    def get_capture_ms(self):
        return self.capture_ms

    def get_capture_fps(self):
        return self.capture_fps
