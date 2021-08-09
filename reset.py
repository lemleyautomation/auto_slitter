import os 
import socket 
import sys
import time
import json

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
        tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tag_server.bind(('', 8090))
        tag_server.listen()
        while True:
            connection, address = tag_server.accept()
            with connection:
                message = connection.recv(1024)
                if message:
                    try:
                        message = json.loads(message)
                        if message['trim'] and message['camera'] and message['module']:
                            file = open('settings.txt', 'w')
                            json.dump(message, file)
                            file.close()
                    except:
                        print('partial message')