import imageio
import pyimgur
import cv2
import os
import stat
import sys


imgur_client_id = os.environ['IMGUR_CLIENT_ID']
imgur_client_secret = os.environ['IMGUR_CLIENT_SECRET']


# places images in input_images directory into a gif and uploads to imgur - optionally delete the images from
# the directory afterwards with the kwarg 'delete=False' or 'delete=false'
def make_gif(file_paths, delete=False):
    images = prepare_images(file_paths)

    # scaled_images = scale_images(images)

    url = generate_and_upload_gif(images)

    if delete:
        delete_input_images()

    return url


# returns the list of full-sized input images for the gif
def prepare_images(file_paths):
    image_file_paths = file_paths# get_input_image_file_paths()

    # change permissions of image files to allow for deletion
    for image_file in image_file_paths:
        # change the image permissions for the purpose of
        # deleting the existing files after resizing them
        os.chmod(image_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    images = []

    # create an array of images rather than an array of image file paths
    for image_file in image_file_paths:
        images.append(imageio.imread(image_file))

    return images


# takes an array of images and scales each one down to a 100px width
def scale_images(images):
    scaled_images = []

    # robust solution for resizing images to have 100 width and maintain scale
    for index, image in enumerate(images):
        r = 100.0 / image.shape[1]
        dim = (100, int(image.shape[0] * r))

        # perform the actual resizing of the image and show it
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        scaled_images.append(resized)

        # re-write image files
        scaled_image_file_string = './output_images/scaled_img' + str(index) + '.jpg'
        imageio.imwrite(scaled_image_file_string, resized)

    output_image_filepaths = []

    for file in os.listdir('./output_images'):
        if file.lower().endswith('.png') or file.lower().endswith('jpg'):
            output_image_filepaths.append('./output_images/' + file)

    for image_file_path in output_image_filepaths:
        os.remove(image_file_path)

    return scaled_images


# generate a gif from the scaled images, upload to imgur, print link to console and delete the local file
def generate_and_upload_gif(images):
    gif_file = './movie.gif'
    imageio.mimsave(gif_file, images, duration=1)

    imgur = pyimgur.Imgur(imgur_client_id)

    uploaded_gif = imgur.upload_image(gif_file, title='Uploaded with PyImgur')

    os.remove(gif_file)
    return uploaded_gif.link


# delete the old image files from the input_images directory
def delete_input_images():
    image_file_paths = get_input_image_file_paths()

    for image_file_path in image_file_paths:
        os.remove(image_file_path)


# return an array of file paths to images in the input_images directory
def get_input_image_file_paths():
    image_file_paths = []

    # place each image .png or .jpg file in ./input_images into an array
    for file in os.listdir('./input_images'):
        if file.lower().endswith('.png') or file.lower().endswith('jpg'):
            image_file_paths.append('./input_images/' + file)

    return image_file_paths


if __name__ == "__main__":
    delete = sys.argv[1].lower()

    make_gif(delete=delete)