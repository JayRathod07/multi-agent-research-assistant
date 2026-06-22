"""
Generates docs/demo.gif from the three app screenshots.
Run once: python docs/make_gif.py
"""
from pathlib import Path
from PIL import Image

DOCS = Path(__file__).parent

frames_cfg = [
    ("screenshot_1.png", 3500),   # overview + metrics — hold 3.5s
    ("screenshot_2.png", 3000),   # research notes    — hold 3s
    ("screenshot_3.png", 4000),   # insights + report — hold 4s
]

TARGET_WIDTH = 1200   # px — good balance of quality vs file size

def resize(img: Image.Image, width: int) -> Image.Image:
    ratio = width / img.width
    return img.resize((width, int(img.height * ratio)), Image.LANCZOS)

frames  = []
delays  = []

for fname, ms in frames_cfg:
    img = Image.open(DOCS / fname).convert("RGB")
    img = resize(img, TARGET_WIDTH)
    frames.append(img)
    delays.append(ms // 10)   # PIL uses 1/100s units

out = DOCS / "demo.gif"
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    duration=delays,
    loop=0,
    optimize=True,
)
kb = out.stat().st_size // 1024
print(f"DONE  Saved {out}  ({kb} KB, {len(frames)} frames)")
