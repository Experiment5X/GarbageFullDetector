import os
import cv2

in_directory = './Training/Not Full2/'
out_directory = './Training/Not Full4/'
files = list([f for f in os.listdir(in_directory)])

for f in files:
    file_path = in_directory + f
    image = cv2.imread(file_path)

    width = image.shape[1]
    height = image.shape[0]
    crop_y = height - width

    image_cropped = image[crop_y:, :]
    image_resized = cv2.resize(image_cropped, (512, 512))

    out_file_path = out_directory + f
    cv2.imwrite(out_file_path, image_resized)

    print('Processed ' + f)

print('Done')

