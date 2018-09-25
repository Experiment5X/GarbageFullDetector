import cv2
import json
import time
import numpy as np
from keras.models import load_model


total_images = 6


image_data = np.zeros((6, 128, 128, 1))
for i in range(1, total_images + 1):
    original_image = cv2.imread('./Evaluate/%d.png' % i)
    adjusted = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY).reshape((128, 128, 1)) / 255

    image_data[i - 1] = adjusted

model = load_model('./Model/model.h5')

time_before = time.time()
result = model.predict(image_data)
time_after = time.time()

print(time_after - time_before)

for i in range(0, total_images):
    if result[i][0] > result[i][1]:
        print('%d. Full' % (i + 1))
    else:
        print('%d. Empty' % (i + 1))
