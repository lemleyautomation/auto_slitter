from tcpIPFunctions import *
from bitFunctions import *
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

def recieve_message(socket):
    end_of_message = False
    fragments = bytearray()
    while not end_of_message:
        part_of_message = socket.recv(1024)
        if not part_of_message:
            end_of_message = True
            continue
        fragments.extend(part_of_message)
        #if len(part_of_message) < 1024:
        #    break
    return fragments

def get_tags(ip_address):
    tags = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pi_socket:
        pi_socket.connect((ip_address, 8090))
        fragments = recieve_message(pi_socket)
        try:
            tags = pickle.loads(fragments)
        except:
            pass
    return tags

def serve():
    hmi = mod.ModbusTcp(ip="192.168.1.45", port=502)
    hmi.connect()
    hmi_registers = hmi.read_registers(0,39)

    all_trim = 0

    pi_tags = {}
    while True:
        hmi_registers = hmi.read_registers(0,39)

        pi_tags[2] = get_tags('192.168.1.22')
        pi_tags[3] = get_tags('192.168.1.23')
        pi_tags[4] = get_tags('192.168.1.24')
        pi_tags[5] = get_tags('192.168.1.25')
        pi_tags[6] = get_tags('192.168.1.26')
        pi_tags[7] = get_tags('192.168.1.27')
        pi_tags[8] = get_tags('192.168.1.28')
        pi_tags[9] = get_tags('192.168.1.29')
        '''
        deviations = ''
        for tag_set in pi_tags.items():
            deviations = deviations + 'pi ' + str(tag_set[1].knife) + ': ' + str(round(tag_set[1].deviation,2)) + '\t'
        print(deviations)
        '''
        for tag_set in pi_tags.items():
            tags = tag_set[1]
            r = (tags.knife-1)*4
            hmi_registers[r] = int(abs((tags.deviation+10)*100))
            hmi_registers[r+1] = int(abs(tags.speed*100))
            hmi_registers[r+2] = int(abs(tags.trim+256))
            hmi_registers[r+3] = write_bit(hmi_registers[r+3], 0, ((now()-tags.heartbeat_timeout) < 3))
            hmi_registers[r+3] = write_bit(hmi_registers[r+3], 1, tags.servo_ready)
            hmi_registers[r+3] = write_bit(hmi_registers[r+3], 2, tags.underspeed)
            
        pw((hmi_registers[-2], hmi_registers[-1]))
        hmi.write_registers(0, hmi_registers[:-2])
        sleep(0.032)    

    hmi.close()