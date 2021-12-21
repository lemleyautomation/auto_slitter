import cv2 as opencv
import numpy
from copy import deepcopy as clone

def getDeviation(images, tags):
    xx = 1
    yy = 0

    [R, G, B] = opencv.split(images.current)

    Rx = opencv.Sobel(R, opencv.CV_32F, xx, yy)
    Gx = opencv.Sobel(G, opencv.CV_32F, xx, yy)
    Bx = opencv.Sobel(B, opencv.CV_32F, xx, yy)

    Ry = opencv.Sobel(R, opencv.CV_32F, yy, xx)
    Gy = opencv.Sobel(G, opencv.CV_32F, yy, xx)
    By = opencv.Sobel(B, opencv.CV_32F, yy, xx)

    Rm, Ra = opencv.cartToPolar(Rx, Ry, angleInDegrees=True)
    Gm, Ga = opencv.cartToPolar(Gx, Gy, angleInDegrees=True)
    Bm, Ba = opencv.cartToPolar(Bx, By, angleInDegrees=True)

    Ra = opencv.normalize(Ra, None, 0,255, opencv.NORM_MINMAX)
    Ga = opencv.normalize(Ga, None, 0,255, opencv.NORM_MINMAX)
    Ba = opencv.normalize(Ba, None, 0,255, opencv.NORM_MINMAX)
    Rm = opencv.normalize(Rm, None, 0,255, opencv.NORM_MINMAX)
    Gm = opencv.normalize(Gm, None, 0,255, opencv.NORM_MINMAX)
    Bm = opencv.normalize(Bm, None, 0,255, opencv.NORM_MINMAX)
    
    derivative = (Ra*Rm) + (Ga*Gm) + (Ba*Bm)
    #images.heat_map = clone(derivative)
    graph = opencv.reduce(derivative, 1, opencv.REDUCE_SUM)

    deviation = (numpy.argmax(graph) - (images.current.shape[0]/2)) / tags.pixels_per_inch

    if abs(deviation - tags.deviation) < 0.2:
        tags.deviation_samples[tags.deviation_index] = deviation
    else:
        tags.deviation_samples[tags.deviation_index] = 0
    
    tags.deviation_index = (tags.deviation_index+1)%len(tags.deviation_samples)
    tags.deviation = numpy.average(tags.deviation_samples)