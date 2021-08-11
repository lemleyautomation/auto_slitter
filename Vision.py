import numpy as np
from Tags import Tags
import cv2
from copy import deepcopy as d
from time import time as now

def process_image(tags,bluring=1, flip=False):

    if not tags.lookup_table.all():
        tags.generateLUT()
    image = tags.current_image

    if not flip:
        xx = 0
        yy = 1
    else:
        xx = 1
        yy = 0

    resized = cv2.GaussianBlur(image, (0,0), bluring)
    [R, G, B] = cv2.split(resized)

    Rx = cv2.Sobel(R, cv2.CV_32F, xx, yy)
    Gx = cv2.Sobel(G, cv2.CV_32F, xx, yy)
    Bx = cv2.Sobel(B, cv2.CV_32F, xx, yy)

    Ry = cv2.Sobel(R, cv2.CV_32F, yy, xx)
    Gy = cv2.Sobel(G, cv2.CV_32F, yy, xx)
    By = cv2.Sobel(B, cv2.CV_32F, yy, xx)

    Rm, Ra = cv2.cartToPolar(Rx, Ry, angleInDegrees=True)
    Gm, Ga = cv2.cartToPolar(Gx, Gy, angleInDegrees=True)
    Bm, Ba = cv2.cartToPolar(Bx, By, angleInDegrees=True)

    Ra = cv2.normalize(Ra, None, 0,255, cv2.NORM_MINMAX)
    Ga = cv2.normalize(Ga, None, 0,255, cv2.NORM_MINMAX)
    Ba = cv2.normalize(Ba, None, 0,255, cv2.NORM_MINMAX)
    Rm = cv2.normalize(Rm, None, 0,255, cv2.NORM_MINMAX)
    Gm = cv2.normalize(Gm, None, 0,255, cv2.NORM_MINMAX)
    Bm = cv2.normalize(Bm, None, 0,255, cv2.NORM_MINMAX)
    
    Rl = cv2.LUT(Ra.astype("uint8"),tags.lookup_table.astype("uint8"))
    Gl = cv2.LUT(Ra.astype("uint8"),tags.lookup_table.astype("uint8"))
    Bl = cv2.LUT(Ra.astype("uint8"),tags.lookup_table.astype("uint8"))

    derivative = (Rm*Rl) + (Gl*Gm) + (Bl*Bm)
    return derivative

def get_graph(derivative_image, bluring=4):
    graph = cv2.reduce(derivative_image, 1, cv2.REDUCE_SUM)
    graph = cv2.GaussianBlur(graph, (0,0), bluring)
    graph[0] = 0
    graph[1] = 0
    graph[2] = 0
    graph[3] = 0
    graph[-1] = 0
    graph[-2] = 0
    graph[-3] = 0
    graph[-4] = 0
    graph = cv2.normalize(graph, None, 0,255, cv2.NORM_MINMAX)
    return graph

def getSpeed(tags):
    try:
        pos = tags.speed * 180
        window = tags.previous_image[:,0:10]
        result = cv2.matchTemplate(tags.current_image, window, cv2.TM_CCOEFF_NORMED)
        spd = np.argmax(result)
        scale = 320/tags.current_image.shape[1]
        seconds_per_frame = tags.image_timestamp-tags.previous_image_timestamp
        inches_travelled = (spd*scale)/tags.pixels_per_inch
        inches_per_second = inches_travelled / seconds_per_frame
        feet_per_minute = inches_per_second * 5

        if feet_per_minute > pos + 10:
            pos = pos + 10
        elif feet_per_minute < pos - 10:
            pos = pos - 10
        
        tags.speed = feet_per_minute / 180
    except:
        pass
    return tags


def getDeviation(tags):
    scale = 256/tags.current_image.shape[0]

    pos = (tags.deviation*tags.pixels_per_inch)/scale

    derivative1 = process_image(tags, 4)
    derivative2 = process_image(tags, 4, True)

    graph1 = get_graph(derivative1,6)
    graph2 = get_graph(derivative2,6)

    indicator1 = np.sum(graph1)
    indicator2 = np.sum(graph2)

    if indicator1 < indicator2 and tags.seal_in >=  0:
        tags.heat_map = derivative1
        graph = graph1
        tags.seal_in= tags.seal_in+1
    else:
        tags.heat_map = derivative2
        graph = graph2
        tags.seal_in = tags.seal_in-1
    
    if tags.seal_in > 10:
        tags.seal_in = 10
    elif tags.seal_in < -10:
        tags.seal_in = -10

    bins = np.zeros(len(graph))
    for i in range(len(graph)-60):
        bins[i+30] = cv2.reduce(graph[i:i+59],0,cv2.REDUCE_SUM)
    
    bins = cv2.GaussianBlur(bins, (0,0), 10)
    
    y = np.argmax(bins) - (tags.current_image.shape[0]/2) + (((tags.trim/32)*tags.pixels_per_inch)/scale)
    if y > pos + 1:
        pos = pos + 2
    elif y < pos - 1:
        pos = pos - 2
    
    tags.deviation = (pos*scale)/tags.pixels_per_inch

    #print(round(y,3), round(pos, 3), round(tags.deviation,3))

    return tags