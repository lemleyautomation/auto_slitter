from tcpIPFunctions import *
import pickle
import pylibmodbus as mod
from threading import Thread, Lock
import socket
import sys
from copy import deepcopy as clone
from time import time as now
from time import sleep
import cv2
import numpy as np
from simple_pyspin import Camera
from Tags import Tags
import Limit_Switch as switch
import Servo
import Vision
from flask import Flask, Response
import hmi_server

#################################################################################
'''
app = Flask(__name__)

def gen_frame():
    frame = cv2.imencode('.jpg', tags.current_image)[1].tobytes()
    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/jpg/image.jpg')
def jpg():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

def image_server():
    app.run(host='192.168.1.26')

Thread(target=image_server).start()
'''
#################################################################################
ip_address = get_IP_address()
knife = int(ip_address[-1])
print("knife #", knife)

if knife == 1:
    print('starting tag server')
    hmi_server.serve()
    exit()

cameras = [ 'none',
            'none',
            '20439783',
            '20439787',
            '20439785',
            '20262959',
            '20439780',
            '20439781',
            '20439779',
            '20439784' ]

tags = Tags()
tag_lock = Lock()

tags.knife = knife

if tags.knife > 4:
    tags.flip_camera = -1

limit_switch = switch.connect()
tags.enabled, limit_switch = switch.get_status(limit_switch, tags.knife)
print('enabled:',tags.enabled)

servo = Servo.connect(tags.knife)
servo_input_registers, servo_output_registers = Servo.read(servo, both=True)
servo_input_registers, servo_output_registers = Servo.configure(servo, servo_input_registers, servo_output_registers)
tags.start_position = Servo.get_position(servo_input_registers)
print('encoder position:', tags.start_position, 'inches')

default_trim = [ 4, #0
                 4, #1
                 4, #2
                 4, #3
                 -12, #4
                 4, #5
                 4, #6
                 4, #7
                 4, #8
                 4] #9

tags.trim = default_trim[tags.knife]

with Camera(cameras[tags.knife]) as camera:
    camera.AcquisitionFrameRate = 30
    camera.start()

    server_thread = Thread(target=tag_server, args=(tags,tag_lock))
    server_thread.start()

    while True:
        start_t = now()
        tags.previous_image = clone(tags.current_image)
        tags.current_image = clone(camera.get_array())

        if tags.knife < 5:
            tags.current_image = cv2.flip(tags.current_image, -1)

        tags.current_image = cv2.resize(tags.current_image, (100,200), cv2.INTER_AREA)
        tags.previous_image_timestamp = tags.image_timestamp
        tags.image_timestamp = now()
        
        start = now()
        tags = Vision.getDeviation(tags)
        tags = Vision.getSpeed(tags)
        tags.underspeed = (tags.speed < 0.10)
        
        enabled, limit_switch = switch.get_status(limit_switch, tags.knife)
        if enabled != tags.enabled:
            tags.start_position = Servo.get_position(servo_input_registers)
            tags.template_image = clone(tags.current_image)
            servo_output_registers = Servo.reset_servo_alarms(servo_output_registers, 1)
        else:
            servo_output_registers = Servo.reset_servo_alarms(servo_output_registers, 0)
        tags.enabled = enabled
        
        servo_input_registers = Servo.read(servo)

        tags.servo_ready = Servo.is_ready(servo_input_registers)
        servo_output_registers = Servo.enable(servo_output_registers, tags.enabled)

        beat_out = Servo.heartbeat_out(servo_output_registers)
        beat_in = Servo.heartbeat_in(servo_input_registers)

        if beat_in != beat_out: 
            tags.heartbeat_timeout = now()

        if (now()-tags.heartbeat_timeout) > 3: 
            tags.heartbeat_timeout = now()
            servo.close()
            servo = Servo.connect(tags.knife)

        servo_output_registers = Servo.set_heartbeat(servo_output_registers, beat_in)
        
        sign_change = ((tags.deviation<=0) != (tags.previous_deviation<0))
        tags.previous_deviation = tags.deviation
        if sign_change:
            tags.deviation = tags.deviation * 1.05
        
        current_position = Servo.get_position(servo_input_registers)
        desired_position = current_position - tags.deviation
        distance_from_start = abs(desired_position-tags.start_position)
        servo_output_registers = Servo.set_position(servo_output_registers, desired_position)

        if tags.speed < 0.2:
            servo_output_registers =  Servo.set_speed(servo_output_registers, 1.5, 3, 3)
        else:
            servo_output_registers =  Servo.set_speed(servo_output_registers, 2, 4, 4)

        if not tags.even:
            servo_output_registers = Servo.start_move(servo_output_registers, False)
            tags.even = True
        else:
            if tags.enabled and abs(tags.deviation) > 0.01 and not tags.underspeed and distance_from_start < 2.5:
                servo_output_registers = Servo.start_move(servo_output_registers, True)
            tags.even = False

        servo.write_registers(0, servo_output_registers)
        #print(round(now()-start_t, 3),round(now()-start,3), round(tags.image_timestamp-tags.previous_image_timestamp, 3))
        #print(round(tags.deviation, 2), '\t', round(tags.speed, 2))
    camera.stop()
    tags.stop_server = True
        
limit_switch.close()
servo.close()