import cv2 as opencv
import numpy

def getSpeed(images, tags):
    #                                       (x, y)
    window = opencv.cvtColor(images.previous, opencv.COLOR_BGR2GRAY)# opencv.resize(images.previous, (200,200), opencv.INTER_AREA)
    template = opencv.cvtColor(images.current, opencv.COLOR_BGR2GRAY)#  opencv.resize(images.current, (200,200), opencv.INTER_AREA)
    #                                       [rox,col]
    result = opencv.matchTemplate(template[0:35,0:90], window[10:30, 5:30], opencv.TM_CCOEFF_NORMED)
    a,b,c,position = opencv.minMaxLoc(result)

    tags.speed_samples[tags.ss_index] = position[0] - 5
    tags.ss_index = (tags.ss_index+1)%len(tags.speed_samples)
    spd = numpy.average(tags.speed_samples)

    seconds_per_frame = images.current_timestamp - images.previous_timestamp
    if seconds_per_frame > 0.01:
        inches_travelled = spd/tags.pixels_per_inch
        inches_per_second = inches_travelled / seconds_per_frame
        feet_per_minute = inches_per_second * 5
        tags.speed = feet_per_minute / 50

def getDeviation(images, tags):
    pos = (tags.deviation*tags.pixels_per_inch)
    images.template = opencv.resize(images.template, (images.current.shape[0], images.current.shape[1]), opencv.INTER_AREA)
    #                                       (x, y)
    window = opencv.cvtColor(images.template, opencv.COLOR_BGR2GRAY)# opencv.resize(images.previous, (200,200), opencv.INTER_AREA)
    template = opencv.cvtColor(images.current, opencv.COLOR_BGR2GRAY)#  opencv.resize(images.current, (200,200), opencv.INTER_AREA)
    #                                       [rox,col]
    result = opencv.matchTemplate(template, window[103:153,:], opencv.TM_CCOEFF_NORMED)
    a,b,c,position = opencv.minMaxLoc(result)
    graph = opencv.normalize(result, None, 0,255, opencv.NORM_MINMAX)
    graph = graph[:,0]
    images.heat_map = result

    travel = position[1] - 128 + 25

    if travel > pos:
        pos = pos + 1
    elif travel < pos:
        pos = pos - 1

    tags.deviation = pos / tags.pixels_per_inch

    return 2*numpy.sum(graph)