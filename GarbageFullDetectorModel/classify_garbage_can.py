import cv2
import json
import time
import logging
import numpy as np
from keras.models import load_model


def initialize_model():
    model = load_model('./Model/model.h5')

    return model


def is_garbage_full(model, image_path):
    image_data = cv2.imread(image_path)

    if image_data is None:
        logging.getLogger().error('Couldnt classify image, not found.')
        return False

    adjusted_image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY).reshape((1, 128, 128, 1)) / 255

    logging.getLogger().info('Max pixel value: ' + str(adjusted_image_data.max()))
    logging.getLogger().info('Mean pixel value: ' + str(adjusted_image_data.mean()))
    logging.getLogger().info('Min pixel value: ' + str(adjusted_image_data.min()))

    result = model.predict(adjusted_image_data)
    return result[0][0] > result[0][1]
