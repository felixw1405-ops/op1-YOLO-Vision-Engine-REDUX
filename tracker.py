import math


def lerp(a, b, t):
    return a + (b - a) * t


class Track:

    NEXT_ID = 0

    def __init__(self, detection):

        self.track_id = Track.NEXT_ID
        Track.NEXT_ID += 1

        self.box = detection["box"]
        self.confidence = detection["confidence"]
        self.cls = detection["class"]

        self.age = 0
        self.missing = 0

        # For future prediction (v5.4)
        self.velocity = (0.0, 0.0)

    def center(self):

        x1, y1, x2, y2 = self.box

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2
        )


class Tracker:

    def __init__(self):

        self.tracks = []

        self.max_missing = 6

        self.match_distance = 75

        self.smoothing = 0.35

    def distance(self, box1, box2):

        x1, y1, x2, y2 = box1
        a1, b1, a2, b2 = box2

        c1 = (
            (x1 + x2) / 2,
            (y1 + y2) / 2
        )

        c2 = (
            (a1 + a2) / 2,
            (b1 + b2) / 2
        )

        return math.hypot(
            c1[0] - c2[0],
            c1[1] - c2[1]
        )

    def smooth_box(self, old_box, new_box):

        return (

            int(lerp(old_box[0], new_box[0], self.smoothing)),

            int(lerp(old_box[1], new_box[1], self.smoothing)),

            int(lerp(old_box[2], new_box[2], self.smoothing)),

            int(lerp(old_box[3], new_box[3], self.smoothing))

        )

    def update(self, detections):

        used = set()

        for track in self.tracks:

            best_index = None
            best_detection = None

            best_distance = self.match_distance

            old_center = track.center()

            for i, detection in enumerate(detections):

                if i in used:
                    continue

                d = self.distance(
                    track.box,
                    detection["box"]
                )

                if d < best_distance:

                    best_distance = d
                    best_detection = detection
                    best_index = i

            if best_detection is None:

                track.missing += 1
                track.age += 1

                continue

            used.add(best_index)

            new_box = best_detection["box"]

            track.box = self.smooth_box(
                track.box,
                new_box
            )

            track.confidence = lerp(
                track.confidence,
                best_detection["confidence"],
                0.30
            )

            track.cls = best_detection["class"]

            new_center = track.center()

            track.velocity = (
                new_center[0] - old_center[0],
                new_center[1] - old_center[1]
            )

            track.age += 1
            track.missing = 0

        for i, detection in enumerate(detections):

            if i in used:
                continue

            self.tracks.append(
                Track(detection)
            )

        self.tracks = [

            track

            for track in self.tracks

            if track.missing <= self.max_missing

        ]

        output = []

        for track in self.tracks:

            output.append({

                "track_id": track.track_id,

                "box": track.box,

                "confidence": track.confidence,

                "class": track.cls,

                "missing": track.missing,

                "age": track.age,

                "velocity": track.velocity

            })

        return output
