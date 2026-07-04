# ✋ AirTask

AI-powered hand gesture recognition system for touchless computer interaction using OpenCV + MediaPipe.

## Modules

### 🖼️ Air Vision Image Navigator
Browse images using hand gestures.
- **Next/Previous Image:** Spread index + middle finger apart (>100px), direction based on which finger leads
- **Zoom In:** Pinch thumb + index close together (<40px)
- **Zoom Out:** Spread thumb + index apart (>100px)
- Reads images from `images/` folder (`.png`, `.jpg`, `.jpeg`)

### ✍️ AirWrite
Draw in the air using your index finger.
- **Draw:** Raise index finger above knuckle line (others down)
- **Select Color:** Hover index finger over top color bar (Red / Green / Blue / Black / Eraser)
- **Stop Drawing:** Lower index finger
- Smoothed cursor tracking for steadier strokes

### 🖱️ HandyMouse
Full gesture-based mouse control.
| Gesture | Action |
|---|---|
| Move hand | Move cursor |
| Index finger up | Left click |
| Middle finger up | Right click |
| Index + middle up | Double click |
| Pinch index + thumb | Drag & drop |
| Hand up / down | Scroll up / down |
| Two hands apart / close | Zoom in / out |
| Two index fingers crossed | Screenshot |
| Fist + move left/right | Switch windows (Alt+Tab) |

## Tech Stack
- **Language:** Python 3.12
- **Libraries:** OpenCV, MediaPipe, NumPy, PyAutoGUI

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Run any module:
```bash
python AirVisionImageNavigator.py
python AirWrite.py
python HandyMouse.py
```

Press `q` to quit any module. Requires a webcam.

## Notes
- Runs on standard webcams, no special hardware needed
- HandyMouse includes PyAutoGUI fail-safe (move cursor to screen corner to force-stop)