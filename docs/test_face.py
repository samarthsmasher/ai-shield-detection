import cv2
import numpy as np

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

# Create a dummy image
img = np.zeros((500, 500, 3), dtype=np.uint8)
cv2.rectangle(img, (200, 200), (300, 300), (255, 255, 255), -1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.1, 4)
print("Faces found:", len(faces))
