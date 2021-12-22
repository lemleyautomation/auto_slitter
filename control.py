from time import time as now
from time import sleep
import network_functions as lan
import Limit_Switch as switch
import bitFunctions as bit
import Servo

from tags import Tags

tags = Tags()

frame_rate = 1/50

limit_switch = switch.connect()
tags.switch_enabled, limit_switch, tags.underspeed = switch.get_status(limit_switch, tags.id)
limit_switch_db = False
limit_switch_transition_time = now()

tags.id = lan.get_ID()

servo_input_registers, servo_output_registers, servo = Servo.connect(tags.id)
tags.servo_enabled = False
tags.start_position = Servo.get_position(servo_input_registers)

#output_file = open("posdata.txt", 'a')

while True:
    loop_time = now()

    tags.switch_enabled, limit_switch, tags.underspeed = switch.get_status(limit_switch, tags.id)

    dev = (tags.deviation*tags.servo_gains[tags.id]) + tags.servo_offsets[tags.id]

    if tags.switch_enabled:
        if not limit_switch_db:
            limit_switch_db = True
            servo_input_registers, servo_output_registers, servo = Servo.connect(tags.id)
            tags.start_position = Servo.get_position(servo_input_registers)
            limit_switch_transition_time = now()
        else:
            servo_input_registers, servo_output_registers = Servo.read(servo, both=True)

        tags.position = Servo.get_position(servo_input_registers)

        #print(bit.bp(servo_input_registers[44]), bit.bp(servo_input_registers[45]), bit.bp(servo_input_registers[46]), bit.bp(servo_input_registers[47]))

        if not Servo.busy(servo_input_registers):
            servo_output_registers = Servo.set_position(servo_output_registers, tags.position - dev)
            servo_output_registers = Servo.set_speed(servo_output_registers, tags.deviation, frame_rate)
            tags.servo_speed = Servo.get_speed_command(servo_output_registers)
            tags.servo_accel = Servo.get_accel_command(servo_output_registers)

        if now()-limit_switch_transition_time > 0.06:
            servo_output_registers = Servo.enable(servo_output_registers)
        else:
            servo_output_registers = Servo.disable(servo_output_registers)

        relative_position = tags.position - tags.start_position

        too_far = ( abs(relative_position) > 3 and ((relative_position>0) == (tags.deviation>0)) ) # 3 inches awawy from where we started

        if  Servo.enabled(servo_input_registers) and not too_far and not tags.underspeed and not Servo.start_move_active(servo_output_registers):
            servo_output_registers = Servo.start_move(servo_output_registers, True)
        else:
            servo_output_registers = Servo.start_move(servo_output_registers, False)

        servo_output_registers = Servo.set_heartbeat(servo_output_registers, servo_input_registers)
        servo.write_registers(0, servo_output_registers)

    else:
        limit_switch_db = False
        servo.close()

    tags.servo_server(lan.servo_upate(tags))
    
    cycle = now()-loop_time
    if cycle < frame_rate:
        sleep( frame_rate - cycle )

limit_switch.close()   

#output_file.close()