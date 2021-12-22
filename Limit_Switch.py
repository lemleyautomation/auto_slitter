import pylibmodbus as mod
import bitFunctions as bit
from time import sleep

def connect():
    limit_switch = None
    while not limit_switch:
        try:
            limit_switch = mod.ModbusTcp(ip="192.168.1.100", port=502)
            limit_switch.connect()
        except:
            limit_switch = None
            #print('connection failed')
            sleep(1)
    return limit_switch

def get_status(limit_switch, index):
    limit_switch_status = 0
    run_command = 0
    try:
        limit_switch_response = limit_switch.read_registers(31,1)[0] #register 31, single word
        limit_switch_status = bit.get_bit(limit_switch_response, index-1)
        run_command = not bit.get_bit(limit_switch_response, 10)
    except:
        limit_switch.close()
        limit_switch = connect()
    return limit_switch_status, limit_switch, run_command