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

    flip_camera = 1

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
    pixels_per_inch = 320/4
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
    