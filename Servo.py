import pylibmodbus as mod
import bitFunctions as bit
from time import sleep

def connect(module_number):
    servo = mod.ModbusTcp(ip=("192.168.1.3" + str(module_number)), port=502)
    servo.connect()
    servo_input_registers, servo_output_registers = read(servo, both=True)
    servo_input_registers, servo_output_registers = configure(servo, servo_input_registers, servo_output_registers)
    return servo_input_registers, servo_output_registers, servo

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
    servo_output_registers[48] = 5                                  # servo decimal places
    servo_output_registers[49] = 1                                  # servo homing type
    servo_output_registers[51] = 1                                  # servo move type
    servo_output_registers[0] = bit.set_bit(servo_output_registers[0], 2)       # start homing
    servo_output_registers[18] = servo_input_registers[48]
    servo_output_registers[19] = servo_input_registers[49]                 # set servo home position to current position
    servo.write_registers(0,servo_output_registers)
    sleep(0.05)
    servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 2)     # stop homing
    servo_output_registers[21], servo_output_registers[20] = bit.get_words(11)  # set acceleration to 11 in/s^2
    servo_output_registers[25], servo_output_registers[24] = bit.get_words(11)  # set deceleration to 11 in/s^2
    servo_output_registers[29], servo_output_registers[28] = bit.get_words(4)   # set servo speed to 4 in/s
    servo.write_registers(0,servo_output_registers)
    
    return servo_input_registers, servo_output_registers

def get_position(servo_input_registers):
    position = bit.get_float(servo_input_registers[49], servo_input_registers[48])
    return position

def set_position(servo_output_registers, desired_position):
    servo_output_registers[37], servo_output_registers[36] = bit.get_words(desired_position) # format desired position from float to modbus words
    return servo_output_registers

def get_position_command(servo_output_registers):
    return bit.get_float(servo_output_registers[37], servo_output_registers[36])

def calc_speed(deviation, frame_rate):
    deviation = abs(deviation)
    acceleration = (2*deviation)/((0.5*frame_rate)**2)
    speed = acceleration * (0.5*frame_rate)
    return speed, acceleration

def set_speed(servo_output_registers, deviation, frame_rate):
    speed, acceleration = calc_speed(deviation, frame_rate)
    servo_output_registers[21], servo_output_registers[20] = bit.get_words(acceleration)
    servo_output_registers[25], servo_output_registers[24] = bit.get_words(acceleration)
    servo_output_registers[29], servo_output_registers[28] = bit.get_words(speed)
    return servo_output_registers

def get_speed_command(servo_output_registers):
    return bit.get_float(servo_output_registers[21], servo_output_registers[20])

def get_accel_command(servo_output_registers):
    return bit.get_float(servo_output_registers[29], servo_output_registers[28])

def start_move(servo_output_registers, status):
    if status:
        servo_output_registers[0] = bit.set_bit(servo_output_registers[0], 3) # set start move to LOW
    else:
        servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 3) # set start move to LOW
    return servo_output_registers

def start_move_active(servo_output_registers):
    return bit.get_bit(servo_output_registers[0], 3)

def reset_servo_alarms(servo_output_registers, value):
    servo_output_registers[0] = bit.write_bit(servo_output_registers[0], 7, value )
    servo_output_registers[0] = bit.write_bit(servo_output_registers[0], 8, value )
    return servo_output_registers

def is_ready(servo_input_registers):
    is_ready = bit.get_bit(servo_input_registers[44], 3)
    return is_ready

def enable(servo_output_registers):
    servo_output_registers[0] = bit.set_bit(servo_output_registers[0], 0)
    return servo_output_registers

def disable(servo_output_registers):
    servo_output_registers[0] = bit.clear_bit(servo_output_registers[0], 0)
    return servo_output_registers

def enabled(servo_input_registers):
    return ( bit.get_bit(servo_input_registers[44], 4) and bit.get_bit(servo_input_registers[44], 3) )

def busy(servo_input_registers):
    return ( bit.get_bit(servo_input_registers[44], 12) or bit.get_bit(servo_input_registers[44] ,13) )

def set_heartbeat(servo_output_registers, servo_input_registers):
    servo_output_registers[2] = bit.write_bit(servo_output_registers[2], 0, bit.get_bit(servo_input_registers[44],0))
    return  servo_output_registers
