from threading import Thread, Lock
from copy import deepcopy as clone
from simple_pyspin import Camera
from time import time as now
from time import sleep

import Limit_Switch as switch
from tcpIPFunctions import *
from Tags import Tags
import hmi_server
import Vision
import Servo

this_trim, this_camera, this_knife = get_settings()
print('knife number:', this_knife)
print('trim value:', this_trim)
print('camera serial number:', this_camera)

if this_knife == 1:
    print('starting tag server')
    hmi_server.serve()
    exit()

tags = Tags()

tags.knife = this_knife
tags.trim = this_trim

limit_switch = switch.connect()
tags.enabled, limit_switch = switch.get_status(limit_switch, tags.knife)
print('enabled:',tags.enabled)

servo = Servo.connect(tags.knife)
servo_input_registers, servo_output_registers = Servo.read(servo, both=True)
servo_input_registers, servo_output_registers = Servo.configure(servo, servo_input_registers, servo_output_registers)
tags.start_position = Servo.get_position(servo_input_registers)
print('encoder position:', tags.start_position, 'inches')

with Camera(this_camera) as camera:
    camera.AcquisitionFrameRate = 16
    camera.start()

    try:
        tags.current_image = clone(camera.get_array())
    except:
        exit() # if image corrupted, exit program. Operating System will restart

    #start sending out tags on a separate thread
    server_thread = Thread(target=tag_server, args=(tags,))
    server_thread.start()

    #start of main program loop
    while True:
        #now() means the current time in microseconds
        start_t = now()

        #the previous image is used by getSpeed() to measure the roller speed
        tags.previous_image = clone(tags.current_image)
        tags.current_image = clone(camera.get_array())

        #cameras 1-4 are mounted on the left side,
        #cameras 5-9 are mounted on the right
        #we flip the image so the program doesn't have to care about that
        if tags.knife < 5:
            tags.current_image = cv2.flip(tags.current_image, -1)

        tags.current_image = cv2.resize(tags.current_image, (200,200), cv2.INTER_AREA)
        tags.previous_image_timestamp = tags.image_timestamp
        tags.image_timestamp = now()
        
        start = now()
        tags = Vision.getDeviation(tags)
        tags = Vision.getSpeed(tags)
        tags.underspeed = (tags.speed < 0.10) # units: % of maximum rollup speed
        
        # lines 77-84 act like a ONE SHOT RISING instruction in a PLC
        # a rising edge of the limit switch: resets servo alarms,
        # sets the relative starting position of the knife,
        # saves an image of the current pattern (for legacy programs)
        # and checks for changes to the trim settings
        enabled, limit_switch = switch.get_status(limit_switch, tags.knife)
        if enabled != tags.enabled:
            tags.trim = get_trim()
            tags.start_position = Servo.get_position(servo_input_registers)
            tags.template_image = clone(tags.current_image)
            servo_output_registers = Servo.reset_servo_alarms(servo_output_registers, 1)
        else:
            servo_output_registers = Servo.reset_servo_alarms(servo_output_registers, 0)
        tags.enabled = enabled
        
        servo_input_registers, servo_output_registers = Servo.read(servo, both=True)
        c = write_float(servo_output_registers[37], servo_output_registers[36], 2)
        print(round(c, 3))

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
        '''
        sign_change = ((tags.deviation<=0) != (tags.previous_deviation<0))
        tags.previous_deviation = tags.deviation
        if sign_change:
            tags.deviation = tags.deviation * 1.05
        '''
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
                #print(round(tags.deviation, 2), '\t', round(current_position, 2), '\t', round(desired_position, 2))
                servo_output_registers = Servo.start_move(servo_output_registers, True)
            tags.even = False

        servo.write_registers(0, servo_output_registers)
        #print(round(now()-start_t, 3),round(now()-start,3), round(tags.image_timestamp-tags.previous_image_timestamp, 3))
        #print(round(tags.deviation, 2), '\t', round(current_position, 2), '\t', round(desired_position, 2))
        #pw((servo_input_registers[44], servo_output_registers[0] ))
    camera.stop()
    tags.stop_server = True
        
limit_switch.close()
servo.close()