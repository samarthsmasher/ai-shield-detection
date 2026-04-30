import sys, io, numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '../models')
from image_inference import predict_image
from PIL import Image

def show(name, result_dict):
    r = result_dict
    icon = "REAL" if r["result"] == "real" else "FAKE"
    print(f"  [{icon}]  {name:<28}  {round(r['confidence']*100,1)}%")

print("=" * 55)
print("  CALIBRATION TEST WITH REAL PHOTO")
print("=" * 55)

# Test 1: Real WhatsApp photo
photo_path = r'C:\Users\sangr\Downloads\IMG_20251217_124505.jpg'
with open(photo_path, 'rb') as f:
    data = f.read()
show(f"WhatsApp photo ({len(data)//1024}KB)", predict_image(data))

# Test 2: Blank white image (should be FAKE)
blank = Image.fromarray((np.ones((224,224,3))*200).astype('uint8'), 'RGB')
buf = io.BytesIO(); blank.save(buf, 'JPEG'); buf.seek(0)
show("Blank/flat image", predict_image(buf.read()))

# Test 3: Pure noise (very textured - should be REAL)
rng = np.random.default_rng(0)
noisy = Image.fromarray(rng.integers(0, 255, (224,224,3)).astype('uint8'), 'RGB')
buf3 = io.BytesIO(); noisy.save(buf3, 'JPEG'); buf3.seek(0)
show("Random noise/texture", predict_image(buf3.read()))

print("=" * 55)
print("  EXPECTED: WhatsApp=REAL, Blank=FAKE, Noise=REAL")
print("=" * 55)
