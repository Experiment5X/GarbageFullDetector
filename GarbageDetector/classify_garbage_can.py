import cv2
import sys
import json
import time
import numpy as np
from keras.models import load_model


def initialize_model():
    model = load_model('./Model/model.h5')

    return model

def is_garbage_full(model, image_path):
    image_data = cv2.imread(image_path)

    if image_data is None:
        print('Couldnt classify image, not found.')
        return False

    adjusted_image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY).reshape((1, 128, 128, 1)) / 255
    cv2.imwrite('adjusted.png', adjusted_image_data.reshape(128, 128, 1) * 255)

    print('Max pixel value: ' + str(adjusted_image_data.max()))
    print('Mean pixel value: ' + str(adjusted_image_data.mean()))
    print('Min pixel value: ' + str(adjusted_image_data.min()))

    result = model.predict(adjusted_image_data)
    return result[0][0] > result[0][1]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: classify_garbage_can.py imagePath')
        exit(-1)
    print('Is garbage full?')

    model = initialize_model()
    print(is_garbage_full(model, sys.argv[1]))