# YOLO Vision Engine v6

A Python-based computer vision application using a custom-trained YOLO model. The project includes screen capture, object detection, tracking, target selection, preview rendering, and macOS pointer-control components.

## Requirements

- macOS
- Python 3.11 recommended
- Git
- The project files, including `models/v5_best.pt`
- Internet access for initial dependency installation

## Installation

Clone the repository:

```bash
git clone https://github.com/felixw1405-ops/op1-YOLO-Vision-Engine
cd "yolo-project v6"
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## macOS Permissions

The application uses screen capture, keyboard input monitoring, and macOS Core Graphics APIs.

Depending on your macOS version and how you launch Python, you may need to grant permissions to Terminal or your Python application under:

**System Settings → Privacy & Security**

Check the relevant permissions:

- Screen Recording or Screen & System Audio Recording
- Accessibility
- Input Monitoring

Restart the application after changing permissions.

## Model Setup

The application uses:

```text
models/v5_best.pt
```

Other included model weights:

- `models/v3.5_best.pt`
- `models/v4.5_best.pt`

Keep the model files in the `models` directory. The application does not need to retrain the model to run with the included weights.

## Running the Application

From the project root, with the virtual environment activated:

```bash
python main.py
```

The application initializes screen capture, the detector, tracker, background worker, keyboard listener, and preview.

## Default Controls

| Key | Action |
|---|---|
| F8 | Toggle active state |
| F9 | Request calibration |
| F10 | Decrease gain |
| F11 | Increase gain |
| Q | Close the preview loop |

The preview can be resized.

## Configuration

Application settings are centralized in `config.py`.

Important settings include:

- `MONITOR`: selected display
- `ROI_W` and `ROI_H`: capture region dimensions
- `AIM_HZ`: main loop target rate
- `RENDER_HZ`: preview render target rate
- `PREVIEW_ENABLED`: enables or disables preview
- `AIM_MODE`: controller mode
- `GAIN` and `STRENGTH`: controller parameters
- `AIM_Y_FRACTION`: vertical target-selection position
- `PREDICT`: enables or disables prediction

Changes to these values should be made in `config.py`.

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | Application entry point and coordination |
| `capture.py` | Screen capture |
| `detector.py` | YOLO model loading and detection |
| `detector_worker.py` | Background detection and tracking processing |
| `tracker.py` | Detection association across frames |
| `targeting.py` | Target selection |
| `aim.py` | macOS pointer-control component |
| `nudger.py` | Additional control component |
| `geometry.py` | Screen and capture-region geometry |
| `draw.py` | Detection and tracking annotations |
| `preview.py` | Preview window and rendering |
| `shared.py` | Thread-safe shared data |
| `metrics.py` | Runtime performance measurements |
| `config.py` | Centralized configuration |
| `train.py` | Model training entry point |
| `debug.py` | Detection debugging |
| `grab.py` | Screen capture utility |
| `latency.py` | Latency measurement utility |

## Dataset

The `dataset/` directory contains the training and validation data and dataset configuration.

The included model weights can be used without retraining.
