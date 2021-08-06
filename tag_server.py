from tcpIPFunctions import *
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

def serve():
    while true:
        sleep(10)