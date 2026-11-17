import time
import collections


class LatencyMonitor:

    def __init__(self):

        self.samples = collections.deque(
            maxlen=120
        )


    def add(self, ms):

        self.samples.append(ms)



    def stats(self):

        if not self.samples:
            return 0,0,0


        data = sorted(self.samples)

        p50=data[len(data)//2]

        p95=data[
            int(len(data)*0.95)
        ]

        avg=sum(data)/len(data)


        return avg,p50,p95



    def print(self):

        avg,p50,p95=self.stats()

        print(
            f"Latency "
            f"AVG:{avg:.1f}ms "
            f"P50:{p50:.1f}ms "
            f"P95:{p95:.1f}ms"
        )
