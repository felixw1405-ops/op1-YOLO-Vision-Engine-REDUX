import threading
import time

from metrics import metrics
from shared import AtomicReference, TrackPacket


class DetectorWorker:

    def __init__(self, capture, detector, tracker):

        self.capture = capture
        self.detector = detector
        self.tracker = tracker

        self.latest_tracks = AtomicReference()

        self.running = False
        self.thread = None

        self.last_frame_id = -1

        self.detect_ms = 0.0

        self.frames_processed = 0

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="DetectorWorker"
        )

        self.thread.start()

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join()

    def _worker(self):

        while self.running:

            packet = self.capture.get_latest()

            if packet is None:
                time.sleep(0.001)
                continue

            # Skip duplicate frame
            if packet.frame_id == self.last_frame_id:
                time.sleep(0.001)
                continue

            self.last_frame_id = packet.frame_id

            detect_start = time.perf_counter()

            # -------------------------
            # YOLO Detection
            # -------------------------
            detections = self.detector.detect(
                packet.frame
            )

            # -------------------------
            # Tracking
            # -------------------------
            tracks = self.tracker.update(
                detections
            )

            detect_end = time.perf_counter()

            self.detect_ms = (
                detect_end - detect_start
            ) * 1000.0

            self.frames_processed += 1

            # -------------------------
            # Metrics
            # -------------------------
            metrics.detect_ms.add(
                self.detect_ms
            )

            pipeline_ms = (
                detect_end
                - packet.capture_timestamp
            ) * 1000.0

            metrics.pipeline_ms.add(
                pipeline_ms
            )

            # -------------------------
            # Publish newest tracks
            # -------------------------
            track_packet = TrackPacket(

                frame_id=packet.frame_id,

                capture_timestamp=packet.capture_timestamp,

                detection_timestamp=detect_end,

                detect_ms=self.detect_ms,

                tracks=tuple(tracks)

            )

            self.latest_tracks.set(
                track_packet
            )

    def get_latest_tracks(self):

        return self.latest_tracks.get()

    def get_detect_ms(self):

        return self.detect_ms

    def get_frames_processed(self):

        return self.frames_processed
