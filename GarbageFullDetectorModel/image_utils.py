import cv2
import random
import numpy as np


def perturb(image):
    if random.random() > 0.8:
        image = add_noise(image)
    if random.random() > 0.5:
        image = mirror(image)
    if random.random() > 0.8:
        image = zoom(image)
    if random.random() > 0.8:
        image = shift_color(image)
    if random.random() > 0.8:
        image = blur(image)
    if random.random() > 0.8:
        image = contrast(image)
    if random.random() > 0.8:
        image = shift_vertical(image)
    if random.random() > 0.8:
        image = shift_horizontal(image)

    return image


def add_noise(image, amount=None):
    """
    Adjust a certain amount of pixels by a random amount between -150 and +150. The image has
    128x128 = 16384

    :param image:
    :param amount:
    :return:
    """
    if amount is None:
        amount = random.randint(100, 750)

    to_return = np.copy(image)
    for i in range(0, amount - 1):
        adjustment = random.randint(-150, 150)

        x = random.randint(0, image.shape[0] - 1)
        y = random.randint(0, image.shape[1] - 1)

        to_return[x][y] += adjustment

    clipped = to_return.clip(0, 255)
    return clipped


def mirror(image):
    return cv2.flip(image, 1)


def zoom(image, percent=10):
    scale = random.randint(0, percent) / 100
    multiplier = 1 + scale
    resized = cv2.resize(image, None, fx=multiplier, fy=multiplier)

    offset = int(128 * scale) - 1
    if offset < 0:
        offset = 0

    cropped = resized[offset:offset + 128, offset:offset + 128]
    return cropped


def shift_color(img, value=None):
    if value is None:
        value = random.randint(-15, 50)

    to_return = np.copy(img)
    if value > 0:
        lim = 255 - value
        to_return[to_return > lim] = 255
        to_return[to_return <= lim] = np.add(to_return[to_return <= lim], value, casting='unsafe')
    else:
        lim = value * -1
        to_return[to_return > lim] = np.add(to_return[to_return > lim], value, casting='unsafe')
        to_return[to_return <= lim] = 0

    return to_return


def blur(image):
    kernel_size = random.randint(0, 2) * 2 + 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def contrast(image, contrast_multiplier=None):
    if contrast_multiplier is None:
        contrast_multiplier = random.random() * 1.2 + 0.8

    image_mean = image.mean()
    contrasty_image = (image - image_mean) * contrast_multiplier + image_mean

    return contrasty_image


def shift_vertical(image, shift_amount=None):
    if shift_amount is None:
        shift_amount = random.randint(-20, 35)

    make_3d = False
    if len(image.shape) == 3:
        make_3d = True
        image = image.reshape(image.shape[0], image.shape[1])

    if shift_amount > 0:
        shifted = np.tile(image[0], (image.shape[1], 1))
        shifted[shift_amount:] = image[:-shift_amount]
    elif shift_amount < 0:
        shift_amount = abs(shift_amount)

        shifted = np.tile(image[-1], (image.shape[1], 1))
        shifted[:-shift_amount] = image[shift_amount:]
    else:
        shifted = np.copy(image)

    if make_3d:
        return shifted.reshape(shifted.shape[0], shifted.shape[1], 1)
    else:
        return shifted


def shift_horizontal(image, shift_amount=None):
    if shift_amount is None:
        shift_amount = random.randint(-25, 25)

    make_3d = False
    if len(image.shape) == 3:
        make_3d = True
        image = image.reshape(image.shape[0], image.shape[1])

    if shift_amount > 0:
        shifted = np.tile(image[:, 0].reshape(image.shape[0], 1), (1, image.shape[0]))
        shifted[:, shift_amount:] = image[:, :-shift_amount]
    elif shift_amount < 0:
        shift_amount = abs(shift_amount)

        shifted = np.tile(image[:, -1].reshape(image.shape[0], 1), (1, image.shape[0]))
        shifted[:, :-shift_amount] = image[:, shift_amount:]
    else:
        shifted = np.copy(image)

    if make_3d:
        return shifted.reshape(shifted.shape[0], shifted.shape[1], 1)
    else:
        return shifted


def edges(image):
    return cv2.Laplacian(image, cv2.CV_64F)

if __name__ == '__main__':
    training_images = np.load('./Training/data.npy')

    # test add noise
    for i in range(0, 10):
        perturbed = add_noise(training_images[i])
        filename = './PerturbedImages/Noise/' + str(i) + '.png'

        cv2.imwrite(filename, perturbed)

    # test mirror
    for i in range(0, 2):
        perturbed = mirror(training_images[i])
        filename = './PerturbedImages/Mirror/' + str(i) + '.png'

    # test zoom
    for i in range(0, 10):
        perturbed = zoom(training_images[i])
        filename = './PerturbedImages/Zoomed/' + str(i) + '.png'

        cv2.imwrite(filename, perturbed)

    # test shift color
    for i in range(0, 10):
        perturbed = shift_color(training_images[i])
        filename = './PerturbedImages/ColorShifted/' + str(i) + '.png'

        print('%d. Mean: %0.02f Std: %0.02f' % (i, perturbed.mean(), perturbed.std()))

        cv2.imwrite(filename, perturbed)

    # test blur
    for i in range(0, 10):
        perturbed = blur(training_images[i])
        filename = './PerturbedImages/Blur/' + str(i) + '.png'

        cv2.imwrite(filename, perturbed)

    # test contrast
    for i in range(0, 10):
        perturbed = contrast(training_images[i])
        filename = './PerturbedImages/Contrast/' + str(i) + '.png'

        cv2.imwrite(filename, perturbed)

    # test shift vertical
    for i in range(0, 10):
        vshifted = shift_vertical(training_images[i].reshape(128, 128))
        filename = './PerturbedImages/ShiftedVertical/' + str(i) + '.png'

        cv2.imwrite(filename, vshifted)

    # test shift horizontal
    for i in range(0, 10):
        hshifted = shift_horizontal(training_images[i].reshape(128, 128))
        filename = './PerturbedImages/ShiftedHorizontal/' + str(i) + '.png'

        cv2.imwrite(filename, hshifted)

    # test edges
    for i in range(0, 10):
        edge = edges(training_images[i].reshape(128, 128))
        filename = './PerturbedImages/Edges/' + str(i) + '.png'

        cv2.imwrite(filename, edge)

    # test perturb
    for i in range(0, 10):
        perturbed = perturb(training_images[i])
        filename = './PerturbedImages/Mixed/' + str(i) + '.png'

        cv2.imwrite(filename, perturbed)
