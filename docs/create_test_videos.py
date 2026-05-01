"""
Creates 5 REAL-looking and 5 FAKE synthetic test videos
for demonstrating the AI Shield Detection System.
Saved to Desktop\AI_Shield_Test_Files\videos\
"""
import sys, os
sys.path.insert(0, '../backend')

import cv2
import numpy as np
from pathlib import Path

OUT_REAL = Path(r"C:\Users\sangr\Desktop\AI_Shield_Test_Files\videos\real")
OUT_FAKE = Path(r"C:\Users\sangr\Desktop\AI_Shield_Test_Files\videos\fake")
OUT_REAL.mkdir(parents=True, exist_ok=True)
OUT_FAKE.mkdir(parents=True, exist_ok=True)

W, H, FPS, SECS = 640, 480, 15, 4   # 4-second videos
FRAMES = FPS * SECS

def make_writer(path):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(str(path), fourcc, FPS, (W, H))

rng = np.random.default_rng(42)

# ─── 5 REAL-looking videos (varied texture, motion, colour) ───────────────────

print("Creating REAL videos...")

# Real 1: natural outdoor scene simulation (varying colour patches + noise)
vw = make_writer(OUT_REAL / "real_01_outdoor_scene.mp4")
for f in range(FRAMES):
    t = f / FRAMES
    frame = rng.integers(0, 255, (H, W, 3), dtype=np.uint8)
    # sky gradient at top
    sky = np.zeros((H//2, W, 3), dtype=np.uint8)
    sky[:, :, 0] = np.clip(100 + int(60*t), 0, 255)   # B
    sky[:, :, 1] = np.clip(160 + int(40*t), 0, 255)   # G
    sky[:, :, 2] = np.clip(220 - int(30*t), 0, 255)   # R
    sky += rng.integers(0, 15, sky.shape, dtype=np.uint8)
    # grass at bottom
    grass = rng.integers(30, 120, (H//2, W, 3), dtype=np.uint8)
    grass[:, :, 1] = np.clip(grass[:, :, 1] + 80, 0, 255)
    frame[:H//2] = sky
    frame[H//2:] = grass
    vw.write(frame)
vw.release()
print("  [1/5] real_01_outdoor_scene.mp4")

# Real 2: people conversation simulation (skin tones + movement)
vw = make_writer(OUT_REAL / "real_02_people_talking.mp4")
for f in range(FRAMES):
    frame = np.full((H, W, 3), [40, 35, 30], dtype=np.uint8)  # dark bg
    cx = int(W*0.4 + 30*np.sin(f*0.3))
    cy = H // 2
    cv2.ellipse(frame, (cx, cy), (80, 110), 0, 0, 360, (140, 150, 200), -1)  # body
    cv2.circle(frame, (cx, cy - 120), 55, (160, 170, 210), -1)                # head
    noise = rng.integers(-12, 12, frame.shape, dtype=np.int16)
    frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    vw.write(frame)
vw.release()
print("  [2/5] real_02_people_talking.mp4")

# Real 3: street traffic simulation (motion blur + varied colours)
vw = make_writer(OUT_REAL / "real_03_street_traffic.mp4")
cars = [(rng.integers(0, W), rng.integers(100, H-100), rng.integers(30, 60)) for _ in range(6)]
for f in range(FRAMES):
    frame = np.full((H, W, 3), [60, 55, 50], dtype=np.uint8)
    frame[H-80:] = [50, 50, 60]   # road
    for i, (x, y, speed) in enumerate(cars):
        nx = int((x + f * speed) % W)
        color = [(0,0,200),(200,0,0),(0,200,0),(200,200,0),(0,200,200),(200,0,200)][i]
        cv2.rectangle(frame, (nx-25, y-15), (nx+25, y+15), color, -1)
    frame += rng.integers(0, 10, frame.shape, dtype=np.uint8)
    vw.write(frame)
vw.release()
print("  [3/5] real_03_street_traffic.mp4")

# Real 4: nature water ripple simulation (complex texture)
vw = make_writer(OUT_REAL / "real_04_nature_water.mp4")
x_grid = np.linspace(0, 4*np.pi, W)
y_grid = np.linspace(0, 4*np.pi, H)
XX, YY = np.meshgrid(x_grid, y_grid)
for f in range(FRAMES):
    t = f * 0.15
    wave = np.sin(XX + t) * np.cos(YY + t*0.7) * 0.5 + 0.5
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:, :, 0] = (wave * 100).astype(np.uint8)        # B water
    frame[:, :, 1] = (wave * 160 + 40).astype(np.uint8)   # G
    frame[:, :, 2] = (wave * 40).astype(np.uint8)         # R dark
    frame += rng.integers(0, 8, frame.shape, dtype=np.uint8)
    vw.write(frame)
vw.release()
print("  [4/5] real_04_nature_water.mp4")

# Real 5: campus / college simulation (structured + noise)
vw = make_writer(OUT_REAL / "real_05_campus_scene.mp4")
for f in range(FRAMES):
    frame = np.full((H, W, 3), [200, 210, 220], dtype=np.uint8)
    # building
    cv2.rectangle(frame, (100, 80), (520, 380), (170, 175, 180), -1)
    # windows
    for row in range(3):
        for col in range(5):
            wx, wy = 130 + col*80, 110 + row*80
            bright = int(200 + 30*np.sin(f*0.2 + col + row))
            cv2.rectangle(frame, (wx, wy), (wx+50, wy+50), (bright, bright, 100), -1)
    # people walking
    px = int((f * 4) % W)
    cv2.circle(frame, (px, 400), 18, (150, 130, 110), -1)
    frame += rng.integers(0, 10, frame.shape, dtype=np.uint8)
    vw.write(frame)
vw.release()
print("  [5/5] real_05_campus_scene.mp4")

# ─── 5 FAKE / Synthetic videos (flat, uniform, artificial) ───────────────────

print("\nCreating FAKE videos...")

# Fake 1: solid single colour (completely flat)
vw = make_writer(OUT_FAKE / "fake_01_solid_color.mp4")
for _ in range(FRAMES):
    frame = np.full((H, W, 3), [120, 80, 200], dtype=np.uint8)
    vw.write(frame)
vw.release()
print("  [1/5] fake_01_solid_color.mp4")

# Fake 2: simple linear gradient (no texture)
vw = make_writer(OUT_FAKE / "fake_02_gradient.mp4")
grad = np.zeros((H, W, 3), dtype=np.uint8)
for x in range(W):
    grad[:, x, 0] = int(x / W * 255)   # B
    grad[:, x, 2] = int((1-x/W) * 180) # R
for _ in range(FRAMES):
    vw.write(grad)
vw.release()
print("  [2/5] fake_02_gradient.mp4")

# Fake 3: checkerboard pattern (repeating tiles)
vw = make_writer(OUT_FAKE / "fake_03_checkerboard.mp4")
board = np.zeros((H, W, 3), dtype=np.uint8)
tile = 40
for r in range(H):
    for c in range(W):
        if (r // tile + c // tile) % 2 == 0:
            board[r, c] = [255, 255, 255]
for _ in range(FRAMES):
    vw.write(board)
vw.release()
print("  [3/5] fake_03_checkerboard.mp4")

# Fake 4: slowly changing flat hue (no texture)
vw = make_writer(OUT_FAKE / "fake_04_flat_hue_shift.mp4")
for f in range(FRAMES):
    h = int((f / FRAMES) * 180)
    hsv = np.full((H, W, 3), [h, 200, 180], dtype=np.uint8)
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    vw.write(frame)
vw.release()
print("  [4/5] fake_04_flat_hue_shift.mp4")

# Fake 5: simple text / graphic (artificial overlay, no photo texture)
vw = make_writer(OUT_FAKE / "fake_05_ai_generated_graphic.mp4")
for f in range(FRAMES):
    frame = np.full((H, W, 3), [15, 15, 15], dtype=np.uint8)
    cv2.circle(frame, (W//2, H//2), 150, (0, 200, 255), -1)
    cv2.rectangle(frame, (W//2-80, H//2-25), (W//2+80, H//2+25), (15, 15, 15), -1)
    cv2.putText(frame, "AI GENERATED", (W//2-100, H//2+10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    vw.write(frame)
vw.release()
print("  [5/5] fake_05_ai_generated_graphic.mp4")

print("\n" + "="*55)
print("  ALL 10 TEST VIDEOS CREATED SUCCESSFULLY!")
print("="*55)
print(f"\n  Real videos: {OUT_REAL}")
print(f"  Fake videos: {OUT_FAKE}")
print("="*55)
