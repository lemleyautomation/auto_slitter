from bitFunctions import *
import pickle
import pylibmodbus as mod
import socket
import sys
from copy import deepcopy as clone
from time import time as now
from time import sleep
from tags import Tags
import network_functions as lan

hmi = mod.ModbusTcp(ip="192.168.1.45", port=502)
hmi.connect()
hmi_registers = hmi.read_registers(0,56)

pi_tags = [ [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False],
            [Tags(),False] ]

io_db = 0
do_db = 0
all_db = False

while True:
    hmi_registers = hmi.read_registers(0,56)

    increase_ofset = hmi_registers[54]
    decrease_ofset = hmi_registers[55]

    for tag_set in pi_tags:
        if tag_set[0].id != 0:
            if (increase_ofset == tag_set[0].id or increase_ofset == 10) and (io_db != increase_ofset or not all_db):
                tag_set[0].servo_offsets[tag_set[0].id] += 0.03
                io_db = increase_ofset
            elif (decrease_ofset == tag_set[0].id or decrease_ofset == 10) and (do_db != decrease_ofset or not all_db):
                tag_set[0].servo_offsets[tag_set[0].id] -= 0.03
                do_db = decrease_ofset

    if increase_ofset == 10 or decrease_ofset == 10:
        all_db = True
    else:
        all_db = False

    if increase_ofset == 0:
        io_db = 0
    
    if decrease_ofset == 0:
        do_db = 0

    pi_tags[2] = lan.update_hmi(pi_tags[2][0], '192.168.1.22')
    pi_tags[3] = lan.update_hmi(pi_tags[3][0], '192.168.1.23')
    pi_tags[4] = lan.update_hmi(pi_tags[4][0], '192.168.1.24')
    pi_tags[5] = lan.update_hmi(pi_tags[5][0], '192.168.1.25')
    pi_tags[6] = lan.update_hmi(pi_tags[6][0], '192.168.1.26')
    pi_tags[7] = lan.update_hmi(pi_tags[7][0], '192.168.1.27')
    pi_tags[8] = lan.update_hmi(pi_tags[8][0], '192.168.1.28')
    pi_tags[9] = lan.update_hmi(pi_tags[9][0], '192.168.1.29')

    for tag_set in pi_tags:
        tags = tag_set[0]
        status = tag_set[1]
        
        if tags.id != 0:
            r = (tags.id-1)*6

            signed_position = tags.position-(42949672.96*(tags.position>21474836.48))
            signed_start_position = tags.start_position - (42949672.96*(tags.start_position>21474836.48))
            relative_position = signed_position - signed_start_position

            position_command = relative_position - tags.deviation

            hmi_registers[r]   = int( abs( (relative_position*100)+1000 ) )
            hmi_registers[r+1] = int( abs( (position_command*100)+1000 ) )
            hmi_registers[r+2] = int( abs( (tags.deviation*100)+1000 ) )
            hmi_registers[r+3] = int( abs( (tags.speed*100)+1000 ) )
            hmi_registers[r+4] = int( abs( (tags.servo_offsets[tags.id]*100)+1000 ) )
            hmi_registers[r+5] = write_bit(hmi_registers[r+5], 0, status)
            hmi_registers[r+5] = write_bit(hmi_registers[r+5], 1, tags.servo_ready)
            hmi_registers[r+5] = write_bit(hmi_registers[r+5], 2, tags.underspeed)
    
    hmi.write_registers(0, hmi_registers[0:54])
    sleep(0.2)    

hmi.close()