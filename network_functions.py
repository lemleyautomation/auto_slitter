'''
Written by Timothey Lemley for Mohawk Industries
September 29, 2021
released as open source
'''
import socket
import pickle
from time import time as now
import struct

from tags import Tags, Images

def get_ID():
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
    ip_address = ip_address[-1]
    dummy_socket.close()
    return int(ip_address)

def send_message(message, socket):
    data = pickle.dumps(message)
    data = struct.pack('>I', len(data)) + data
    socket.sendall(data)

def recv_msg(socket):
    # Read message length and unpack it into an integer
    packet = socket.recv(4)
    length = struct.unpack('>I', packet)[0]
    # Read the message data
    data = bytearray()
    while len(data) < length:
        packet = socket.recv(length - len(data))
        if not packet:
            return None
        data.extend(packet)
    message = pickle.loads(data)
    return message

def update_server(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as local:
            #local.settimeout(0.01)
            local.connect(('localhost', 8090))
            send_message( message, local)
            return recv_msg(local)
    except:
        print("comms error")
        return None

def update_hmi(tags, IPaddress):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as local:
            local.settimeout(0.01)
            local.connect((IPaddress, 8090))
            send_message( ('hmi', tags), local)
            return [recv_msg(local), True]
    except:
        return [tags, False]

def vision_update(tags):
    response = update_server(('vision', tags))
    if response == None:
        return tags
    else:
        return response

def servo_upate(tags):
    response = update_server(('servo', tags))
    if response == None:
        return tags
    else:
        return response