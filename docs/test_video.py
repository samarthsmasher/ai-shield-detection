import requests
import os
import numpy as np
import cv2

# Create a small valid MP4 video
video_path = "test_vid.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_path, fourcc, 10.0, (160, 120))
for i in range(20):
    frame = np.random.randint(0, 256, (120, 160, 3), dtype=np.uint8)
    out.write(frame)
out.release()

# Upload the video to the API
with open(video_path, "rb") as f:
    files = {"file": ("test_vid.mp4", f, "video/mp4")}
    resp = requests.post("http://127.0.0.1:8000/api/detect/video", files=files)

print("Video Response:")
print(resp.status_code)
print(resp.text)

os.remove(video_path)
