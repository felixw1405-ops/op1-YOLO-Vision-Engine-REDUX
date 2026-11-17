import cv2

_buf = None


def _text(frame, s, y, color):
    cv2.putText(frame, s, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)


def render(cfg, frame_packet, track_packet, active, stats, draw_fn):
    global _buf

    src = frame_packet.frame
    h, w = src.shape[:2]

    pw = min(cfg.PREVIEW_WIDTH, w)
    ph = int(h * pw / w)

    if _buf is None or _buf.shape[:2] != (ph, pw):
        _buf = cv2.resize(src, (pw, ph), interpolation=cv2.INTER_AREA)
    else:
        cv2.resize(src, (pw, ph), dst=_buf, interpolation=cv2.INTER_AREA)
    small = _buf

    if cfg.DRAW_BOXES and track_packet is not None:
        sx, sy = pw / w, ph / h
        scaled = []
        for t in track_packet.tracks:
            st = dict(t)
            x1, y1, x2, y2 = t["box"]
            st["box"] = (int(x1 * sx), int(y1 * sy), int(x2 * sx), int(y2 * sy))
            scaled.append(st)
        small = draw_fn(small, scaled)

    status = "STATUS: ON (ACTIVE)" if active else "STATUS: OFF (IDLE)"
    _text(small, status, 25, (0, 255, 0) if active else (0, 0, 255))
    _text(small, f"Capture FPS : {stats.get('capture_fps', 0):.1f}", 50, (0, 255, 0))
    _text(small, f"Render FPS : {stats.get('render_fps', 0):.1f}", 75, (0, 255, 0))
    _text(small, f"Detect : {stats.get('detect_ms', 0):.1f} ms", 100, (255, 255, 0))
    _text(small, f"Pipeline : {stats.get('pipeline_ms', 0):.1f} ms", 125, (0, 200, 255))
    _text(small, f"ROI {cfg.ROI_W:.2f}x{cfg.ROI_H:.2f}  GAIN {cfg.GAIN:.3f}", 150, (200, 200, 200))

    cv2.imshow(cfg.WINDOW_TITLE, small)
