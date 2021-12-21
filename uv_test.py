import cv2 as opencv
import numpy
from time import time as now
from copy import deepcopy as clone
from simple_pyspin import Camera

import network_functions as lan
from tags import Images, Tags

import sys
sys.path.insert(0, './programs')
from uv import getDeviation

images = Images()
tags = Tags()

tags.id = lan.get_ID() # 1-9 starting from wall side and counting up to forklift side
tags.camera_serial = tags.cam_serials[tags.id]

switch_on = False

with Camera(tags.camera_serial) as camera:
    camera.AcquisitionFrameRate = 60 #frames per second
    camera.start()
    
    try:
        images.current = clone(camera.get_array())
    except:
        exit() # if image corrupted, exit program. Operating System will restart

    #start of main program loop
    while True:
        #now() means the current time in microseconds
        start_t = now()

        #the previous image is used by getSpeed() to measure the roller speed
        images.previous = clone(images.current)
        images.previous_timestamp = images.current_timestamp
        images.current = clone(camera.get_array())
        images.current_timestamp = now()

        # effectively a rising edge 'one-shot' that takes a new template image at the moment of knife engagement
        if tags.switch_enabled and not switch_on:
            images.template = clone(images.current)
            opencv.imwrite('template.Bmp', images.template)
            switch_on = True
        elif not tags.switch_enabled:
            switch_on = False

        #cameras 1-4 are mounted on the left side,
        #cameras 5-9 are mounted on the right
        if tags.id < 5:
            images.current = opencv.flip(images.current, -1)

        start = now()
        getDeviation(images, tags)
        
        tags.vision_server(lan.vision_update(tags))

        lan.update_server(('images', images))
        #print( round((now() - start_t),3), round((now() - start),3) )
        #print( round(1/(now() - start_t),3), round((now() - start),3) )
        
    camera.stop()