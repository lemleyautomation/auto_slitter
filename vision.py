import cv2 as opencv
import numpy
from time import time as now
from copy import deepcopy as clone
from simple_pyspin import Camera

import sys
sys.path.insert(0, './programs')

from template_matching      import getSpeed
from template_matching      import getDeviation as d0
from sobel_lut              import getDeviation as d1
from sobel_lut_inverted     import getDeviation as d2
programs = [d1, d2]

import network_functions as lan
from tags import Images, Tags

images = Images()
tags = Tags()

tags.id = lan.get_ID() # 1-9 starting from wall side and counting up to forklift side
tags.camera_serial = tags.cam_serials[tags.id]

switch_on = False

with Camera(tags.camera_serial) as camera:
    camera.AcquisitionFrameRate = 30 #frames per second
    camera.start()

    try:
        images.current = clone(camera.get_array())
        images.template = opencv.resize(images.current, (256,256), opencv.INTER_AREA)
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
        if tags.switch_enabled and not switch_on:
            images.template = clone(images.current)
            opencv.imwrite('template.Bmp', images.template)
            switch_on = True
        elif not tags.switch_enabled:
            switch_on = False

        #cameras 1-4 are mounted on the left side,
        #cameras 5-9 are mounted on the right
        #we flip the image so the program doesn't have to care about that
        if tags.id < 5:
            images.current = opencv.flip(images.current, -1)
        images.current = opencv.resize(images.current, (256,256), opencv.INTER_AREA)
        
        start = now()
        getSpeed(images,tags)
        tags.underspeed = (tags.speed < 0.10) # units: % of maximum rollup speed
        tags.program = 1
        programs[tags.program](images, tags)
        tags.deviation = tags.deviation * 4
        
        #print(round(tags.speed,2), '\t', tags.deviation)
        #print(tags.votes, tags.program, round(now() - start,3))
        #print( round(now() - start_t,3), '\t\t', round(now() - start,3))
        tags.vision_server(lan.vision_update(tags))

        lan.update_server(('images', images))
        
    camera.stop()