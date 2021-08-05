import pylibmodbus as mod
import bitFunctions as bit
from time import sleep

def connect(module_number):
    servo = mod.ModbusTcp(ip=("192.168.1.3" + str(module_number)), port=502)
    servo.connect()
    return servo

def read(servo, both=False):
    servo_input_registers = 0
    servo_output_registers = 0
    try:
        if both:
            servo_input_registers = servo.read_input_registers(0,54) #register 0, 54 words
            servo_output_registers = servo.read_registers(0,54) #register 0, 54 words
        else:
            servo_input_registers = servo.read_input_registers(0,54) #register 0, 54 words
    except:
        pass
    if both:
        return servo_input_registers, servo_output_registers
    else:
        return servo_input_registers

def configure(servo, servo_input_registers, servo_output_registers):
    servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 0)     # make sure servo is off
    servo_output_registers[0] = bit.set_bit(servo_output_registers[0], 2)       # start homing
    servo_output_registers[48] = 2                                  # servo decimal places
    servo_output_registers[49] = 1                                  # servo homing type
    servo_output_registers[51] = 1                                  # servo move type
    servo_output_registers[18] = servo_input_registers[48]
    servo_output_registers[19] = servo_input_registers[49]                 # set servo home position to current position
    servo.write_registers(0,servo_output_registers)
    sleep(0.5)
    servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 2)     # stop homing
    servo_output_registers[20] = 400                                # set acceleration to 4 in/s^2
    servo_output_registers[21] = 0
    servo_output_registers[24] = 400                                # set deceleration to 4 in/s^2
    servo_output_registers[25] = 0
    servo_output_registers[28] = 200                                # set servo speed to 2 in/s
    servo_output_registers[29] = 0
    servo.write_registers(0,servo_output_registers)
    
    return servo_input_registers, servo_output_registers

def get_position(servo_input_registers):
    position = bit.write_float(servo_input_registers[49], servo_input_registers[48], 2)
    return position

def set_position(servo_output_registers, desired_position):
    servo_output_registers[37], servo_output_registers[36] = bit.write_32_bit_word(desired_position, 2) # format desired position from float to modbus words
    return servo_output_registers

def set_speed(servo_output_registers, speed_command, acceleration_command, deceleration_command):
    servo_output_registers[20] = int(acceleration_command*100)
    servo_output_registers[21] = 0
    servo_output_registers[24] = int(deceleration_command*100)
    servo_output_registers[25] = 0
    servo_output_registers[28] = int(speed_command*100)
    servo_output_registers[29] = 0
    return servo_output_registers

def start_move(servo_output_registers, status):
    if status:
        servo_output_registers[0] = bit.set_bit(servo_output_registers[0], 3) # set start move to LOW
    else:
        servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 3) # set start move to LOW
    return servo_output_registers

def reset_servo_alarms(servo_output_registers, value):
    servo_output_registers[0] = bit.write_bit(servo_output_registers[0], 7, value )
    servo_output_registers[0] = bit.write_bit(servo_output_registers[0], 8, value )
    return servo_output_registers

def is_ready(servo_input_registers):
    is_ready = bit.get_bit(servo_input_registers[44], 3)
    return is_ready

def enable(servo_output_registers, limit_switch_status):
    servo_output_registers[0] = bit.write_bit(servo_output_registers[0], 0, limit_switch_status) # servo enable
    return servo_output_registers

def heartbeat_in(servo_input_registers):
    return bit.get_bit(servo_input_registers[44],0)

def heartbeat_out(servo_output_registers):
    servo_output_registers[2] = bit.get_bit(servo_output_registers[2],0)
    return servo_output_registers

def set_heartbeat(servo_output_registers, value):
    servo_output_registers[2] = bit.write_bit(servo_output_registers[2], 0, value) #rebound heartbeat
    return  servo_output_registers
