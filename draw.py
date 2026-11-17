import cv2


# How far ahead to predict.
# Current tracker velocity is measured in pixels/update,
# so this is a simple multiplier for now.
PREDICTION_FACTOR = 0.35


def draw(frame, detections):
    """
    Draw tracked detections onto the frame.

    Prediction is applied only while rendering so the tracker
    itself always keeps the true measured position.
    """

    for detection in detections:

        x1, y1, x2, y2 = detection["box"]

        # -----------------------------
        # Prediction
        # -----------------------------
        vx, vy = detection.get("velocity", (0.0, 0.0))

        dx = int(vx * PREDICTION_FACTOR)
        dy = int(vy * PREDICTION_FACTOR)

        x1 += dx
        y1 += dy
        x2 += dx
        y2 += dy

        confidence = detection["confidence"]
        track_id = detection.get("track_id", -1)
        missing = detection.get("missing", 0)

        # -----------------------------
        # Track state color
        # -----------------------------
        if missing == 0:
            color = (0, 255, 0)      # Green
        elif missing <= 2:
            color = (0, 255, 255)    # Yellow
        elif missing <= 4:
            color = (0, 165, 255)    # Orange
        else:
            color = (0, 0, 255)      # Red

        # -----------------------------
        # Bounding box
        # -----------------------------
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        # -----------------------------
        # Center point (helps visualize prediction)
        # -----------------------------
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        cv2.circle(
            frame,
            (center_x, center_y),
            3,
            color,
            -1
        )

        # -----------------------------
        # Label
        # -----------------------------
        label = f"ID:{track_id} | {confidence:.2f}"

        if missing > 0:
            label += f" | M:{missing}"

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

        # -----------------------------
        # Velocity vector (debug)
        # -----------------------------
        end_x = int(center_x + vx * 2)
        end_y = int(center_y + vy * 2)

        cv2.arrowedLine(
            frame,
            (center_x, center_y),
            (end_x, end_y),
            (255, 0, 255),
            2,
            tipLength=0.3
        )

    return frame
