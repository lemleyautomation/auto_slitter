'''
Written by Timothey Lemley for Mohawk Industries
September 29, 2021
released as open source

this program is essentially a dummy server to test the control program

'''
import socket
import pickle

deviation = 0.03

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tag_server:
    tag_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tag_server.bind(('', 8090))
    tag_server.listen()
    while True:
        connection, address = tag_server.accept()
        with connection:
            print(address)
            connection.sendall(pickle.dumps(deviation))