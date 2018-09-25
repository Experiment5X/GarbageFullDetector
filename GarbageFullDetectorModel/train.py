import cv2
import random
import numpy as np
from clr_callback import CyclicLR
from image_utils import perturb
from keras.models import Sequential
from keras.layers import Conv2D, Dense, BatchNormalization, MaxPooling2D, Flatten, Dropout
from keras.losses import binary_crossentropy
from keras.callbacks import BaseLogger
from keras.optimizers import *
from keras.preprocessing.image import ImageDataGenerator


training_images = np.load('./Training/data.npy')
training_labels = np.load('./Training/labels.npy')


print('Found ' + str(len(training_images)) + ' total images')


validation_split = 0.25

training_images_max = training_images.max()
print('Image max = ' + str(training_images_max))
upper_range = int((1 - validation_split) * training_images.shape[0])

print('Upper range: ' + str(upper_range))

example_image_count = 6
for i in range(0, example_image_count):
    cv2.imwrite('./ExampleImages/%d.png' % i, training_images[i])


def batch_generator():
    batch_size = 32

    batch_images = np.zeros((batch_size, 128, 128, 1))
    batch_labels = np.zeros((batch_size, 2))

    # generator loop
    while True:
        # generate all the images in the batch
        for i in range(0, batch_size):
            # select a random image
            rand_image_index = random.randint(0, upper_range)

            rand_image = np.copy(training_images[rand_image_index])
            rand_label = np.copy(training_labels[rand_image_index])

            batch_images[i] = (perturb(rand_image) / training_images_max).reshape(128, 128, 1)
            batch_labels[i] = rand_label

        yield batch_images, batch_labels


model = Sequential()
# model.add(Conv2D(64, (3, 3), activation='relu', input_shape=(128, 128, 1)))
# model.add(MaxPooling2D())
# model.add(Conv2D(64, (3, 3), activation='relu'))
# model.add(MaxPooling2D())
# model.add(Dense(50, activation='relu'))
# model.add(Flatten())
# model.add(Dense(2, activation='softmax'))

model.add(Conv2D(64, (3, 3), activation='relu', input_shape=(128, 128, 1)))
model.add(MaxPooling2D())
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D())
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Flatten())
model.add(Dense(50, activation='relu'))
model.add(Dense(2, activation='softmax'))

model.compile(loss=binary_crossentropy, optimizer=Adam(), metrics=['accuracy'])

# model.fit(training_images, training_labels, batch_size=16, epochs=14, callbacks=[BaseLogger()], validation_split=0.25, verbose=2)


image_generator = ImageDataGenerator(
    # rotation_range=20,
    zoom_range=0.05,
    channel_shift_range=0.05,
)
# model.fit_generator(image_generator.flow(training_images, training_labels, batch_size=32), epochs=7,
#                    steps_per_epoch=len(training_images) / 32)
validation_x = training_images[upper_range + 1:] / training_images_max
validation_y = training_labels[upper_range + 1:]
validation_data = zip(validation_x, validation_y)

print('Have ' + str(len(validation_x)) + ' validation images')

# clr = CyclicLR(mode='triangular2')

history = model.fit_generator(batch_generator(), len(training_images) / 16, epochs=30, verbose=2)
validation_result = model.evaluate(validation_x, validation_y, 16, verbose=2)

print('Validation Loss: %0.4f\tValidation Accuracy: %0.2f%%' % (validation_result[0], validation_result[1] * 100))

model.save('./Model/model.h5')
print('Wrote Model')
