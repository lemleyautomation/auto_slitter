import cv2 as opencv
import numpy as np

class Tags:
    knife = 0
    enabled = False
    enabled_toggle = False
    deviation = 0
    previous_deviation = 1
    speed = 0
    underspeed = True
    program = 0
    trim = 0
    increase_trim = False
    decrease_trim = False
    increase_trim_all = False
    decrease_trim_all = False
    trim_command_debounce = False
    Knife_alignment = 128

    dev_samples = np.zeros(4)
    dev_head = 0
    def getAverage(self, dev):
        self.dev_samples[self.dev_head] = dev
        self.dev_head = (self.dev_head+1)%len(self.dev_samples)
        return np.average(self.dev_samples)

    spd_samples = np.zeros(4)
    spd_head = 0
    def getAverages(self, spd):
        self.spd_samples[self.spd_head] = spd
        self.spd_head = (self.spd_head+1)%len(self.spd_samples)
        return np.average(self.spd_samples)

    stop_server = False

    heartbeat_timeout = 0
    servo_ready = False
    servo_position = 0
    start_position = 0
    even = False

    seal_in = 0
    current_image = None
    heat_map = None
    previous_image = None
    template_image = None
    pixels_per_inch = 312/4
    image_timestamp = 0
    previous_image_timestamp = 0

    lookup_table = np.zeros(255)
    def generateLUT(self):
        self.lookup_table = []
        for i in range(256):
            self.lookup_table.append(i/20.37)
        self.lookup_table = np.array(self.lookup_table)
        self.lookup_table = (-128*np.cos(self.lookup_table))+128
        for i in range(len(self.lookup_table)):
            if self.lookup_table[i] < 248:
                self.lookup_table[i] = 0

        '''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
            tag_server.connect(('192.168.1.200', 8090))
            message = pickle.dumps(tags)
            tag_server.sendall(message)
            #response
            tag_server.shutdown(1)
        '''

class recieveTags:
    update_trim = 0
    