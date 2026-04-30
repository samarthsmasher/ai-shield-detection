import sys, io
sys.path.insert(0, '../models')
import numpy as np
from PIL import Image
from image_inference import _predict_heuristic

def test(name, arr):
    img = Image.fromarray(arr.astype('uint8'), 'RGB')
    r = _predict_heuristic(img)
    icon = "REAL" if r["result"] == "real" else "FAKE"
    print(f"  [{icon}]  {name:30s}  confidence={r['confidence']*100:.1f}%")

print("=" * 65)
print("  HEURISTIC CALIBRATION TEST")
print("=" * 65)

rng = np.random.default_rng(42)

# 1. Real natural photo — lots of variation
real = rng.integers(0, 255, (224, 224, 3))
for i in range(224):
    real[i, :, 0] = np.clip(real[i, :, 0] + i, 0, 255)
test("Natural noisy photo", real)

# 2. Typical WhatsApp photo — defined regions + texture
wp = np.zeros((224, 224, 3), dtype=np.int32)
wp[:112, :, :] = rng.integers(100, 200, (112, 224, 3))  # sky
wp[112:, :, :] = rng.integers(20, 100, (112, 224, 3))   # ground
wp += rng.integers(-15, 15, (224, 224, 3))
wp = np.clip(wp, 0, 255)
test("WhatsApp/camera photo", wp)

# 3. Portrait with skin tones + background
portrait = rng.integers(150, 220, (224, 224, 3))  # skin
portrait[0:60, :, :] = rng.integers(50, 180, (60, 224, 3))  # hair
portrait += rng.integers(-20, 20, (224, 224, 3))
portrait = np.clip(portrait, 0, 255)
test("Portrait photo", portrait)

# 4. AI-generated (flat colour, minimal texture)
ai_flat = np.zeros((224, 224, 3), dtype=np.int32)
ai_flat[:, :, 0] = 180; ai_flat[:, :, 1] = 120; ai_flat[:, :, 2] = 200
ai_flat += rng.integers(-3, 3, (224, 224, 3))  # tiny noise
ai_flat = np.clip(ai_flat, 0, 255)
test("AI-gen (smooth flat)", ai_flat)

# 5. Blank image
blank = np.ones((224, 224, 3), dtype=np.int32) * 200
test("Blank/uniform image", blank)

print("=" * 65)
print("  REAL expected for tests 1-3, FAKE expected for tests 4-5")
print("=" * 65)
