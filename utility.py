import os 
import socket 
import sys
import time
import json
import pickle

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
        tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tag_server.bind(('', 8089))
        tag_server.listen()
        while True:
            connection, address = tag_server.accept()
            with connection:
                message = connection.recv(1024)
                if message:
                    try:
                        message = pickle.loads(message)
                        if message['trim']:
                            if message['trim'] > -33 and message['trim'] < 33:
                                file_path = os.path.dirname(os.getcwd()) + '/settings/settings.txt'

                                file = open(file_path)
                                settings = json.load(file)
                                file.close()

                                settings['trim'] = message['trim']

                                file = open(file_path, 'w')
                                json.dump(settings, file)
                                file.close()
                    except:
                        print('partial message')