from time import time as now
import numpy
import cv2 as opencv
from copy import deepcopy as clone

class Tags:
    id = 0

    switch_enabled = False
    servo_enabled = False
    servo_ready = False
    position = 0.0
    start_position = 0.0

    speed = 0.0
    speed_samples = numpy.zeros(5)
    ss_index = 0
    deviation = 0.0
    underspeed = True

    offset = 0
    camera_serial = '20439780'
    pixels_per_inch = 80
    
    program = 1
    #votes = [14, 15, 14]
    votes = None

    def elect_program(self, indicators):
        if self.votes == None:
            self.votes = [ ((len(indicators)*10)/2)-1 for indicator in indicators]
            self.votes[0] += 1

        winner = numpy.argmax(self.votes)
        strongest = numpy.argmin(indicators)

        if winner != strongest:
            self.votes[winner] -= 1
            self.votes[strongest] += 1
        else:
            local_votes = clone(self.votes)
            local_votes[winner] = 0
            runner_up = numpy.argmax(local_votes)
            if local_votes[runner_up] > 0:
                self.votes[runner_up] -= 1
                self.votes[winner] += 1

        winner = numpy.argmax(self.votes)
        self.program = winner

    def servo_client(self, tags):
        self.switch_enabled = tags.switch_enabled
        self.servo_enabled = tags.servo_enabled
        self.servo_ready = tags.servo_ready
        self.position = tags.position
        self.start_position = tags.start_position
        return self

    def servo_server(self, tags):
        self.speed = tags.speed
        self.deviation = tags.deviation
        self.underspeed = tags.underspeed

    def vision_client(self, tags):
        self.speed = tags.speed
        self.deviation = tags.deviation
        self.program = tags.program
        self.underspeed = tags.underspeed
        self.votes = tags.votes
        return self

    def vision_server(self, tags):
        self.offset = tags.offset
        self.pixels_per_inch = tags.pixels_per_inch
        self.camera_serial = tags.camera_serial

class Images:
    width = 320
    height = 256
    current = numpy.zeros((height,width,3), dtype=numpy.uint8)
    previous = numpy.zeros((height,width,3), dtype=numpy.uint8)
    template = numpy.zeros((height,width,3), dtype=numpy.uint8)
    current_timestamp = now()
    previous_timestamp = now()
    heat_map = numpy.zeros((height,width,3), dtype=numpy.uint8)