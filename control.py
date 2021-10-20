from time import time as now
from time import sleep
import network_functions as lan
import Limit_Switch as switch
import bitFunctions as bit
import Servo

from tags import Tags

id = lan.get_ID()

tags = Tags()

limit_switch = switch.connect()
tags.switch_enabled, limit_switch = switch.get_status(limit_switch, id)
limit_switch_db = False
limit_switch_transition_time = now()

servo_input_registers, servo_output_registers, servo = Servo.connect(id)
tags.servo_enabled = False
tags.start_position = Servo.get_position(servo_input_registers)

while True:
    loop_time = now()

    tags.switch_enabled, limit_switch = switch.get_status(limit_switch, id)

    print(tags.deviation)

    if tags.switch_enabled:
        if not limit_switch_db:
            limit_switch_db = True
            servo_input_registers, servo_output_registers, servo = Servo.connect(id)
            tags.start_position = Servo.get_position(servo_input_registers)
            limit_switch_transition_time = now()
        else:
            servo_input_registers, servo_output_registers = Servo.read(servo, both=True)

        tags.position = Servo.get_position(servo_input_registers)

        servo_output_registers = Servo.set_position(servo_output_registers, tags.position - (tags.deviation*0.8))

        #print( bit.bp(servo_input_registers[44]), bit.bp(servo_input_registers[47]), bit.bp(servo_output_registers[0]), bit.bp(servo_output_registers[2]), round(tags.deviation,2))

        if now()-limit_switch_transition_time > 0.06:
            servo_output_registers = Servo.enable(servo_output_registers)
        else:
            servo_output_registers = Servo.disable(servo_output_registers)

        relative_position = tags.position - tags.start_position

        too_far = ( abs(relative_position) > 3 and ((relative_position>0) == (tags.deviation>0)) ) # 3 inches awawy from where we started

        if not too_far and Servo.enabled(servo_input_registers) and not Servo.start_move_active(servo_output_registers) and not Servo.busy(servo_input_registers):
            servo_output_registers = Servo.start_move(servo_output_registers, True)
        else:
            servo_output_registers = Servo.start_move(servo_output_registers, False)

        servo_output_registers = Servo.set_heartbeat(servo_output_registers, servo_input_registers)
        servo.write_registers(0, servo_output_registers)

    else:
        limit_switch_db = False
        servo.close()

    tags.servo_server(lan.servo_upate(tags))
    #print(round(tags.speed,2), '\t', tags.deviation)
    
    cycle = now()-loop_time
    if cycle < 0.03125:
        sleep( 0.03125 - cycle )

limit_switch.close()   