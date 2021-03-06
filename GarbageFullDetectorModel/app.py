import os
import cv2
import time
import json
import sched
import boto3
import logging
import picamera
import coloredlogs
import numpy as np
import classify_garbage_can
import make_gif
from threading import Lock
from queue import LifoQueue


resolution = 128
# should really read this in from settings so state is preservered over run sessions
garbage_last_full = False
garbage_last_full_true_state = False
first_run = True
images = LifoQueue()

images_lock = Lock()

coloredlogs.install()

# all intervals are in seconds
record_interval = 4
record_priority = 2

detect_interval = 6
detect_priority = 3

# it's rare so it's okay to have a high priority, and want to make sure that it executes
# the record doesn't realllly have to be exact
cleanup_interval = 60
cleanup_priority = 1


def initialize_camera(camera):
    camera.resolution = (resolution, resolution)
    time.sleep(0.2)

def take_picture(camera, out_dir='./captured_images/'):
    """ Take a picture with the camera and write the image as a PNG to 
        a specified directory. The name of the image is the current
        unix timestamp.
    
    Arguments:
        camera {PiCamera} -- The camera to take the picture with
    
    Keyw    ord Arguments:
        out_dir {str} -- Path to directory to save the picture to (default: {'./captured_images/'})
    
    Returns:
        tuple(2) -- (current_timestamp, saved_image_path)
    """

    output = np.empty((resolution, resolution, 3), dtype=np.uint8)
    camera.capture(output, 'bgr')
    
    cur_time = time.time()
    cur_time_str = str(cur_time)
    out_image_name = out_dir + cur_time_str + '.png'
    cv2.imwrite(out_image_name, output)

    logging.getLogger().info('Took image and wrote to ' + out_image_name)

    return (cur_time, out_image_name)


def write_garbage_status(is_garbage_full):
    settings = get_current_settings()
    settings['isGarbageFull'] = is_garbage_full

    write_current_setttings(settings)

def detect(s, model):
    global garbage_last_full_true_state, garbage_last_full, first_run

    image_timestamp, image_path = list(images.queue)[-1]
    logging.getLogger().info(image_timestamp)
    logging.getLogger().info('Got newest image, detecting...')

    garbage_currently_full = classify_garbage_can.is_garbage_full(model, image_path)
    logging.getLogger().warning('Garbage currently full => ' + str(garbage_currently_full))
    logging.getLogger().warning('Garbage last full => ' + str(garbage_last_full))

    if first_run:
        first_run = False
    elif garbage_currently_full and garbage_last_full:
        logging.getLogger().warning('Detected garbage full')
        if not garbage_last_full_true_state or first_run:
            settings = get_current_settings()

            notification_delay = int(settings['timeToNotify'])
            logging.getLogger().info('Read notification delay as: ' + str(notification_delay))
            
            s.enter(notification_delay, 1, notify, argument=[image_timestamp])
            logging.getLogger().info('Scheduled notification')

            write_garbage_status(True)
        
        garbage_last_full_true_state = True
    elif not garbage_currently_full and not garbage_last_full:
        logging.getLogger().warning('Detected garbage NOT full')
        if garbage_last_full_true_state or first_run:
            write_garbage_status(False)

        garbage_last_full_true_state = False
    
    garbage_last_full = garbage_currently_full

    s.enter(detect_interval, detect_priority, detect, argument=[s, model])
    logging.getLogger().info('Scheduled another detection')

def record(s, camera):
    """Repeatedly take pictures, putting their information into a global queue
    
    Arguments:
        camera {PiCamera} -- The camera object to take a picture with
    """

    image_info = take_picture(camera)
    images.put(image_info)

    s.enter(record_interval, record_priority, record, argument=[s, camera])

def get_current_settings():
    with open('/opt/GarbageDetector/settings.store.json') as f:
        return json.load(f)

def get_detector_settings():
    if os.path.isfile('/opt/GarbageDetector/detector-settings.store.json'):
        with open('/opt/GarbageDetector/detector-settings.store.json') as f:
            return json.load(f)
    else:
        return {
            'numbersToNotify': '',
            'timeToNotify': '10',
            'numbers': {}
        }

def write_current_setttings(settings):
    with open('/opt/GarbageDetector/settings.store.json', 'w') as f:
        return json.dump(settings, f)

def write_detector_setttings(settings):
    with open('/opt/GarbageDetector/detector-settings.store.json', 'w') as f:
        return json.dump(settings, f)

def update_sns_subscribers():
    logging.getLogger().info('Updating sns subscribers')
    cur_settings = get_current_settings()
    cur_numbers = cur_settings['numbersToNotify'].split(':')

    detector_settings = get_detector_settings()
    detector_numbers = detector_settings['numbersToNotify'].split(':')

    # check if there are any new numbers that need to be subscribed to the topic
    sns_client = boto3.client('sns')
    for num in cur_numbers:
        if not num in detector_numbers and num != '':
            logging.getLogger().info('Found new number: ' + num)
            response = sns_client.subscribe(TopicArn='arn:aws:sns:us-east-1:051948470005:garbage_full', Protocol='sms', Endpoint=num) 
            logging.getLogger().info('Response from AWS: ' + str(response))

            # save the subscription arn to settings
            detector_settings['numbers'][num] = response
    
    # check if there are any numbers that need to be unsubscribed
    for num in detector_numbers:
        if not num in cur_numbers and num != '' and num in detector_settings['numbers']:
            logging.getLogger().info('Found stale number: ' + num)
            
            num_attributes = detector_settings['numbers'][num]
            if num_attributes is None or not 'SubscriptionArn' in num_attributes:
                logging.getLogger().info('No subscription ARN found for ' + num)
            else:
                arn = num_attributes['SubscriptionArn']
                sns_client.unsubscribe(SubscriptionArn=arn)

    # write the settings
    detector_settings['numbersToNotify'] = cur_settings['numbersToNotify']
    write_detector_setttings(detector_settings)

def notify(detected_time):
    update_sns_subscribers()

    logging.getLogger().info('Getting images for notificiation....')

    # find the index of the image that was first detected as a full garbage
    logging.getLogger().critical('notify: trying to aquire images_lock')
    images_lock.acquire(True)
    logging.getLogger().critical('notify: successfully acquired images_lock')
    all_images = list(images.queue)

    index = -1
    while abs(index) <= len(all_images) and all_images[index][0] > detected_time:
        index -= 1
    logging.getLogger().info('Found detected image index to be: ' + str(index))

    image_paths = []

    logging.getLogger().info('Total image count: ' + str(len(all_images)))

    i = -3
    while i < 0 and abs(index + i) <= len(all_images):
        image_paths.append(all_images[index + i][1])
        i += 1
    logging.getLogger().info('Got 3 empty images')

    image_paths.append(all_images[index][1])

    i = 0
    while i < 3 and abs(index + i) <= len(all_images):
        image_paths.append(all_images[index + i][1])
        i += 1
    logging.getLogger().info('Got 3 full images')

    images_lock.release()
    logging.getLogger().critical('notify: released images_lock')

    logging.getLogger().info('Image path info: ' + str(image_paths))
    logging.getLogger().info('Image path count=' + str(len(image_paths)))
    logging.getLogger().info('Done getting images for notification')
    
    logging.getLogger().info('Making and uploading gif...')
    gif_url = make_gif.make_gif(image_paths)
    logging.getLogger().warning('Here\'s the culprit: ' + gif_url)

    # sns_client = boto3.client('sns')
    # sns_client.publish(TopicArn='arn:aws:sns:us-east-1:051948470005:garbage_full', Message='Your garbage is full. Culrpit: ' + gif_url)
    logging.getLogger().info('Sent notification out with aws')

def cleanup(s):
    global images

    logging.getLogger().critical('cleanup: trying to aquire images_lock')
    images_lock.acquire(True)
    logging.getLogger().critical('cleanup: successfully acquired images_lock')
    all_images = list(images.queue)

    # need to keep around the pictures long enough for the notifier to still have them
    # could pass some of them to the notify function, but some are in the future
    if len(all_images) < 20:
        images_lock.release()
        logging.getLogger().critical('cleanup: released images_lock 1')

        logging.getLogger().info('Cleaning skipped, less than 20 images total. Found ' + str(len(all_images)))
    else:
        logging.getLogger().error('Cleaning up, total found: ' + str(len(all_images)))

        # replace the existing images queue
        to_keep = all_images[-20:]
        to_keep.reverse()

        new_images = LifoQueue()
        for image_info in to_keep:
            new_images.put(image_info)

        images = new_images

        images_lock.release()
        logging.getLogger().critical('cleanup: released images_lock 2')

        # delete all of the files
        for _, image_path in all_images[:-20]:
            os.remove(image_path)

        logging.getLogger().error('Deleted ' + str(len(all_images[:-20])) + ' old images')

    s.enter(cleanup_interval, cleanup_priority, cleanup, argument=[s])

    logging.getLogger().error('Scheduled another cleanup')

# schedule the first record function to start the infinite recording thread
with picamera.PiCamera() as camera:
    if camera is None:
        logging.getLogger().info('Could not detect camera')
        exit(-1)

    logging.getLogger().info('Detected camera')
    initialize_camera(camera)
    logging.getLogger().info('Initialized camera')

    s = sched.scheduler(time.time, time.sleep)

    s.enter(0, record_priority, record, argument=[s, camera])
    logging.getLogger().info('Scheduled recording')

    model = classify_garbage_can.initialize_model()
    logging.getLogger().info('Initialized garbage can model')

    s.enter(0, detect_priority, detect, argument=[s, model])
    logging.getLogger().info('Scheduled detection')

    s.enter(0, cleanup_priority, cleanup, argument=[s])
    logging.getLogger().error('Scheduled cleanup')
    
    s.run()
