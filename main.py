import time

import cv2
from pynput import keyboard as kb

import config as cfg
from capture import ScreenCapture
from detector import Detector
from tracker import Tracker
from detector_worker import DetectorWorker
from draw import draw
from metrics import metrics

from geometry import Geometry
from aim import Aim
from targeting import Targeter
import preview


def _key_name(key):
    if isinstance(key, kb.Key):
        return key.name
    return getattr(key, "char", None)


def main():
    capture = ScreenCapture(
        monitor=cfg.MONITOR,
        search_width=cfg.ROI_W,
        search_height=cfg.ROI_H,
    )
    geom = Geometry(capture.monitor, cfg.ROI_W, cfg.ROI_H, cfg.CROP_CENTERED)
    aim = Aim(cfg, geom)
    targeter = Targeter(cfg)
    worker = DetectorWorker(capture, Detector(), Tracker())

    state = {"active": False}

    def on_press(key):
        action = {
            cfg.KEY_TOGGLE: "toggle",
            cfg.KEY_CALIBRATE: "calib",
            cfg.KEY_GAIN_DOWN: "gain_down",
            cfg.KEY_GAIN_UP: "gain_up",
        }.get(_key_name(key))

        if action == "toggle":
            state["active"] = not state["active"]
            if state["active"]:
                aim.warp()
            else:
                aim.reset()
                targeter.reset()
            print(f">> Aim: {'ON' if state['active'] else 'OFF'}")
        elif action == "calib":
            aim.request_calibration()
        elif action == "gain_down":
            aim.gain = max(0.005, aim.gain / 1.1)
            print(f"[gain] {aim.gain:.4f}")
        elif action == "gain_up":
            aim.gain = min(20.0, aim.gain * 1.1)
            print(f"[gain] {aim.gain:.4f}")

    listener = kb.Listener(on_press=on_press)
    listener.start()
    capture.start()
    worker.start()

    if cfg.PREVIEW_ENABLED:
        cv2.namedWindow(cfg.WINDOW_TITLE, cv2.WINDOW_NORMAL)   # resizable
        cv2.resizeWindow(cfg.WINDOW_TITLE, cfg.PREVIEW_WIDTH,
                         int(cfg.PREVIEW_WIDTH * cfg.ROI_H / cfg.ROI_W))

    print(
        f"monitor={capture.monitor}  ROI={cfg.ROI_W}x{cfg.ROI_H}  "
        f"centre=({geom.centre[0]:.0f},{geom.centre[1]:.0f})  mode={cfg.AIM_MODE}"
    )

    tick = 1.0 / cfg.AIM_HZ
    render_interval = 1.0 / cfg.RENDER_HZ
    last_render = 0.0
    last_print = time.perf_counter()
    last_key = None

    try:
        while True:
            t0 = time.perf_counter()

            frame_packet = capture.get_latest()
            track_packet = worker.get_latest_tracks()

            if state["active"] and frame_packet is not None and track_packet is not None:
                key = getattr(track_packet, "frame_id", None)
                if key is None:
                    key = id(track_packet)

                if key != last_key:
                    last_key = key
                    ref = aim.ref()
                    err = targeter.select(
                        track_packet, geom, frame_packet.frame.shape, ref
                    )
                    if err:
                        if aim.calibrating:
                            aim.calibrate(err[0])
                        else:
                            frame_t = getattr(frame_packet, "capture_timestamp", None)
                            aim.step(err[0], err[1], frame_t)

            if cfg.PREVIEW_ENABLED and frame_packet is not None:
                now = time.perf_counter()
                if now - last_render >= render_interval:
                    last_render = now
                    metrics.tick_render()
                    preview.render(
                        cfg, frame_packet, track_packet,
                        state["active"], metrics.summary(), draw,
                    )
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

            if time.perf_counter() - last_print >= 1.0 / cfg.LOG_HZ:
                s = metrics.summary()
                print(
                    f"Capture FPS: {capture.get_capture_fps():.1f} | "
                    f"Capture: {capture.get_capture_ms():.1f} ms | "
                    f"Detect: {s.get('detect_ms', 0):.1f} ms | "
                    f"Pipeline: {s.get('pipeline_ms', 0):.1f} ms"
                )
                last_print = time.perf_counter()

            sleep = tick - (time.perf_counter() - t0)
            if sleep > 0:
                time.sleep(sleep)

    finally:
        listener.stop()
        worker.stop()
        capture.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
