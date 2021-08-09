import pylibmodbus as mod
import numpy as np
from time import time as now
from time import sleep
from threading import Thread, Lock
import socket
import sys
from bitFunctions import *
import pickle
from Tags import Tags, recieveTags
from copy import deepcopy as clone
import cv2
from flask import Flask 

def get_IP_address():
    # Unless we try to connect to something, the IP address we get will just be 'localhost'
    # but the connection doesn't have to work, it just needs to bind to the ethernet driver
    dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dummy_socket.settimeout(0.001)
    try:
        dummy_socket.connect(('10.10.10.10', 1))
    except:
        pass
    ip_address = dummy_socket.getsockname()
    ip_address = ip_address[0]
    dummy_socket.close()
    return ip_address

def tag_server(tags,tag_lock):
    while not tags.stop_server:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
                tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                tag_server.settimeout(5)
                tag_server.bind(('', 8090))
                tag_server.listen(10)
                while not tags.stop_server:
                    try:
                        connection, address = tag_server.accept()
                        with connection:
                            connection.sendall(pickle.dumps(tags))
                    except socket.timeout:
                        pass
        except:
            print('tag server rebooting')
            
    print('tag server shutdown')
    return