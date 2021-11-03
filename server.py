'''
Written by Timothey Lemley for Mohawk Industries
September 29, 2021
released as open source
'''
from Limit_Switch import connect
import socket
import pickle
from time import time as now
from os import system as command_line

from tags import Tags, Images
import network_functions as lan

images = Images()
tags = Tags()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
    tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tag_server.bind(('', 8090))
    tag_server.listen()
    while True:
        connection, address = tag_server.accept()
        with connection:
            try:
                message = lan.recv_msg(connection)
            except:
                continue
            
            #print(message[0], address)

            if message[0] == 'servo':
                tags = tags.servo_client(message[1])
            elif message[0] == 'vision':
                tags.vision_client(message[1])
            elif message[0] == 'images':
                images = message[1]
            elif message[0] == 'monitor':
                lan.send_message((tags,images), connection)
                continue
            elif message[0] == 'hmi':
                tags.hmi_client(message[1])
            elif message[0] == 'restart':
                command_line('sudo reboot now')
            
            try:
                lan.send_message(tags, connection)
            except:
                pass