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

def tag_error_check(module):
    tags = Tags()

    try:
        tags = get_tags('192.168.1.2' + str(module))
    except:
        pass

    if tags.knife == 0:
        tags.knife = module
    return tags

def increaseTrim(pi, trim):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
            tag_server.connect(('192.168.1.2'+str(pi), 8089))
            settings = {}
            settings['trim'] = trim + 1
            tag_server.sendall(pickle.dumps(settings))
    except:
        pass

def decreaseTrim(pi, trim):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
            tag_server.connect(('192.168.1.2'+str(pi), 8089))
            settings = {}
            settings['trim'] = trim - 1
            tag_server.sendall(pickle.dumps(settings))
    except:
        pass

def serve():
    hmi = mod.ModbusTcp(ip="192.168.1.45", port=502)
    hmi.connect()
    hmi_registers = hmi.read_registers(0,39)

    increase_trim = 0
    decrease_trim = 0

    pi_tags = {}
    while True:
        hmi_registers = hmi.read_registers(0,40)

        pi_tags[2] = tag_error_check(2)
        pi_tags[3] = tag_error_check(3)
        pi_tags[4] = tag_error_check(4)
        pi_tags[5] = tag_error_check(5)
        pi_tags[6] = tag_error_check(6)
        pi_tags[7] = tag_error_check(7)
        pi_tags[8] = tag_error_check(8)
        pi_tags[9] = tag_error_check(9)

        if increase_trim == 0 and hmi_registers[38] != 0 and hmi_registers[38] < 10:
            increaseTrim(hmi_registers[38], pi_tags[hmi_registers[38]].trim)
        if decrease_trim == 0 and hmi_registers[39] != 0 and hmi_registers[39] < 10:
            decreaseTrim(hmi_registers[39], pi_tags[hmi_registers[39]].trim)
        increase_trim = hmi_registers[38]
        decrease_trim = hmi_registers[39]

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

        #pw((hmi_registers[37], hmi_registers[38]))
        hmi.write_registers(0, hmi_registers[0:36])
        sleep(0.062)    

    hmi.close()