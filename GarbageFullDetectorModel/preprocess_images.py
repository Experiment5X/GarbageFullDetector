import os
import cv2
import numpy as np


image_size = 128


def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    if value > 0:
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] = np.add(v[v <= lim], value, casting='unsafe')
    else:
        lim = value * -1
        v[v > lim] = np.add(v[v > lim], value, casting='unsafe')
        v[v <= lim] = 0

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return grey


def crop_to_middle(image):
    height, width = image.shape[:2]

    y = int((height - width) / 2)
    return image[y: y+width, 0:width]


in_directory1 = './Training/Full3'
in_directory2 = './Training/Not Full3'
out_directory = './Training/'

files = list([(True, f) for f in os.listdir(in_directory1)])
files.extend(list([(False, f) for f in os.listdir(in_directory2)]))

images = np.zeros((len(files) * 1, image_size, image_size, 1))
labels = np.zeros((len(files) * 1, 2))

np.random.shuffle(files)
for index, pair in enumerate(files):
    is_full, filename = pair
    if is_full:
        file_path = os.path.join(in_directory1, filename)
    else:
        file_path = os.path.join(in_directory2, filename)

    if os.path.isfile(file_path):
        image = cv2.imread(file_path)

        cropped = crop_to_middle(image)
        resized = cv2.resize(cropped, (image_size, image_size), interpolation=cv2.INTER_AREA)
        greyscale = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        flipped = cv2.flip(greyscale, 1)

        darkened = increase_brightness(resized, -35)
        lightened = increase_brightness(resized, 60)

        images[index * 1] = greyscale.reshape(128, 128, 1)
        # images[index * 2 + 1] = flipped.reshape(128, 128, 1)
        # images[index * 4 + 2] = darkened.reshape(128, 128, 1)
        # images[index * 4 + 3] = lightened.reshape(128, 128, 1)

        if is_full:
            labels[index * 1][0] = 1
            # labels[index * 2 + 1][0] = 1
            # labels[index * 2 + 2][0] = 1
            # labels[index * 2 + 3][0] = 1
        else:
            labels[index * 1][1] = 1
            # labels[index * 2 + 1][1] = 1
            # labels[index * 4 + 2][1] = 0
            # labels[index * 4 + 3][1] = 0

        print('Processed ' + filename)

data_path = os.path.join(out_directory, 'data')
np.save(data_path, images)

labels_path = os.path.join(out_directory, 'labels')
np.save(labels_path, labels)

print('Found ' + str(len(images)) + ' images')
print('Wrote all data to ' + data_path)
print('Done')
