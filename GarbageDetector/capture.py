import cv2
import time
import picamera
import numpy as np

with picamera.PiCamera() as camera:
	output = np.empty((512, 512, 3), dtype=np.uint8)
	camera.resolution = (512, 512)
	# camera.iso = 800
	# camera.exposure_mode = 'off'
	# camera.shutter_speed = 600000

	print('Initializing...')
	time.sleep(0.2)

	while True:
		input('\nWaiting...')

		print('Capturing...')
		camera.capture(output, 'bgr')

		print('Got the image')

		filename = './training_images/%s.png' % str(time.time())
		cv2.imwrite(filename, output)
		print('Wrote image to '  + filename)
