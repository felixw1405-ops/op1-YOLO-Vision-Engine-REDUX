import collections
import time


class Metric:

    def __init__(self, history=120):
        self.samples = collections.deque(maxlen=history)

    def add(self, value):
        self.samples.append(float(value))

    def latest(self):
        if not self.samples:
            return 0.0
        return self.samples[-1]

    def average(self):
        if not self.samples:
            return 0.0
        return sum(self.samples) / len(self.samples)

    def minimum(self):
        if not self.samples:
            return 0.0
        return min(self.samples)

    def maximum(self):
        if not self.samples:
            return 0.0
        return max(self.samples)

    def percentile(self, p):
        if not self.samples:
            return 0.0

        data = sorted(self.samples)

        index = int((len(data) - 1) * p)

        return data[index]


class Metrics:

    def __init__(self):

        self.capture_ms = Metric()
        self.detect_ms = Metric()
        self.pipeline_ms = Metric()

        self.capture_fps = Metric()
        self.render_fps = Metric()

        self.last_render = time.perf_counter()

    def tick_render(self):

        now = time.perf_counter()

        delta = now - self.last_render

        if delta > 0:
            self.render_fps.add(1.0 / delta)

        self.last_render = now

    def summary(self):

        return {

            "capture_ms":
                self.capture_ms.latest(),

            "detect_ms":
                self.detect_ms.latest(),

            "pipeline_ms":
                self.pipeline_ms.latest(),

            "capture_fps":
                self.capture_fps.latest(),

            "render_fps":
                self.render_fps.latest(),

            "capture_avg":
                self.capture_ms.average(),

            "detect_avg":
                self.detect_ms.average(),

            "pipeline_avg":
                self.pipeline_ms.average(),
        }


metrics = Metrics()
