"""Quick validation test on actual Kaggle face images."""
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MODELS_DIR = r"c:\2ST Sem Study Material & Assignment\ASEP 2\chat gpt\models"
sys.path.insert(0, MODELS_DIR)

from PIL import Image
from image_inference import predict_image

real_dir = r"c:\2ST Sem Study Material & Assignment\ASEP 2\chat gpt\real-vs-fake\valid\real"
fake_dir = r"c:\2ST Sem Study Material & Assignment\ASEP 2\chat gpt\real-vs-fake\valid\fake"

real_paths = glob.glob(os.path.join(real_dir, "*.jpg"))[:50]
fake_paths = glob.glob(os.path.join(fake_dir, "*.jpg"))[:50]

print("=" * 56)
print("  Kaggle Model — Real Face Photos Validation Test")
print(f"  Model: 191.6 MB (trained on 100k images)")
print("=" * 56)

real_correct = 0
for p in real_paths:
    img = Image.open(p).convert("RGB")
    buf = io.BytesIO(); img.save(buf, "JPEG"); buf.seek(0)
    r = predict_image(buf.getvalue())
    if r["result"] == "real":
        real_correct += 1

print(f"  REAL faces: {real_correct}/50 correct  ({real_correct*2}%)")

fake_correct = 0
for p in fake_paths:
    img = Image.open(p).convert("RGB")
    buf = io.BytesIO(); img.save(buf, "JPEG"); buf.seek(0)
    r = predict_image(buf.getvalue())
    if r["result"] == "fake":
        fake_correct += 1

print(f"  FAKE faces: {fake_correct}/50 correct  ({fake_correct*2}%)")
total = real_correct + fake_correct
print(f"  Overall   : {total}/100 = {total}%")
print("=" * 56)
