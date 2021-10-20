import cv2 as opencv
import numpy

lookup_table = []

def generateLUT():
    if len(lookup_table) > 1:
        return lookup_table
    
    lut = []
    for i in range(256):
        lut.append(i/20.37)
    lut = numpy.array(lut)
    lut = (-128*numpy.cos(lut))+128
    for i in range(len(lut)):
        if lut[i] < 248:
            lut[i] = 0
    return lut

def process_image(images, bluring=1):

    lookup_table = generateLUT()
    image = images.current
   
    xx = 1
    yy = 0

    resized = opencv.GaussianBlur(image, (0,0), bluring)
    [R, G, B] = opencv.split(resized)

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
    
    Rl = opencv.LUT(Ra.astype("uint8"), lookup_table.astype("uint8"))
    Gl = opencv.LUT(Ra.astype("uint8"), lookup_table.astype("uint8"))
    Bl = opencv.LUT(Ra.astype("uint8"), lookup_table.astype("uint8"))

    derivative = (Rm*Rl) + (Gl*Gm) + (Bl*Bm)
    return derivative

def get_graph(derivative_image, bluring=4):
    graph = opencv.reduce(derivative_image, 1, opencv.REDUCE_SUM)
    graph = opencv.GaussianBlur(graph, (0,0), bluring)
    graph[0] = 0
    graph[1] = 0
    graph[2] = 0
    graph[3] = 0
    graph[0:10] = 0
    graph[-1] = 0
    graph[-2] = 0
    graph[-3] = 0
    graph[-4] = 0
    graph = opencv.normalize(graph, None, 0,255, opencv.NORM_MINMAX)
    return graph


def getDeviation(images, tags):
    pos = tags.deviation*tags.pixels_per_inch

    graph = None


    derivative = process_image(images, 4)
    graph = get_graph(derivative,6)
    indicator = numpy.sum(graph)
    #images.heat_map = derivative
    
    bins = numpy.zeros(len(graph))
    for i in range(len(graph)-60):
        bins[i+30] = opencv.reduce(graph[i:i+59],0,opencv.REDUCE_SUM)
    
    bins = opencv.GaussianBlur(bins, (0,0), 10)
    
    y = numpy.argmax(bins) - (images.current.shape[0]/2) + (((tags.offset/32)*tags.pixels_per_inch))
    if y > pos+1:
        pos += 1
    elif y < pos-1:
        pos -= 1
    
    tags.deviation = pos/tags.pixels_per_inch

    #print(round(y,3), round(pos, 3), round(tags.deviation,3))
    #print('\t\t', tags.deviation, indicator)
    return indicator