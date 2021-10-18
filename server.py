'''
Written by Timothey Lemley for Mohawk Industries
September 29, 2021
released as open source
'''
from Limit_Switch import connect
import socket
import pickle
from time import time as now

from tags import Tags, Images
import network_functions as lan

images = Images()
tags = Tags()
tags.id = lan.get_ID()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
    tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tag_server.bind(('', 8090))
    tag_server.listen()
    while True:
        connection, address = tag_server.accept()
        with connection:
            message = lan.recv_msg(connection)
            
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
            
            lan.send_message(tags, connection)