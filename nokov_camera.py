import socket
import numpy as np
import cv2
import threading
import struct
import time
import ctypes
from ctypes import *

class NOKOVCamera():
    streamSource = None
    camera = None
    ip = ""
    port = 6553
    __BUFF_LEN = 1500
    def  __init__(self, index):
        self.imgSize = (1024,2048)
        self.running = True
        self.recvImg = np.zeros(self.imgSize, dtype=np.uint8)
        self.points = np.zeros((1024, 3), dtype=np.float32)
        # self.points_y = np.zeros((1024,), dtype=np.float32)
        # self.points_z = np.zeros((1024,), dtype=np.float32)
        self.SDKdll = ctypes.CDLL("./dll/x64/nokov.dll")
        self.SDKdll.nokovInit(index)
        self.recvTh = threading.Thread(target=self.readImage, daemon=True)
        self.recvTh.start()
        self.pointTh = threading.Thread(target=self.readPoint, daemon=True)
        self.pointTh.start()
    
    def readImage(self):
        while self.running:
            self.SDKdll.getImage(self.recvImg.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))
            time.sleep(0.5)
    
    def readPoint(self):
        while self.running:
            num = ctypes.c_int(0)
            self.SDKdll.getPoint(
                self.points[:, 0].ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                self.points[:, 1].ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                self.points[:, 2].ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.byref(num)
            )
            # print(num.value)
            time.sleep(0.01)

    def read(self):
        return [self.running, self.recvImg]

    def setExpose(self, expose):
        # exposeValue = math.pow(2, expose) * 1000000
        # setExposureTime(self.camera, exposeValue)
        pass


    def get(self, status):
        if status == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.imgSize[0]
        elif status == cv2.CAP_PROP_FRAME_WIDTH:
            return self.imgSize[1]

    def release(self):
        self.SDKdll.nokovClose()
        time.sleep(1)
        self.running = False       