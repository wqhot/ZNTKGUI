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
        self.showImg = np.zeros(self.imgSize, dtype=np.uint8)
        self.pointNum = 0
        self.drawPointFlag = False
        self.points_x = np.zeros((1024,), dtype=np.float32)
        self.points_y = np.zeros((1024,), dtype=np.float32)
        self.points_z = np.zeros((1024,), dtype=np.float32)
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
    
    def enableDraw(self, flag):
        self.drawPointFlag = flag

    def readPoint(self):
        while self.running:
            num = ctypes.c_int(0)
            self.SDKdll.getPoint(
                self.points_x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                self.points_y.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                self.points_z.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                ctypes.byref(num)
            )
            self.showImg = cv2.cvtColor(self.recvImg, cv2.COLOR_GRAY2RGB)
            if num.value >= 0:
                self.pointNum = num.value
            # print(num.value)
            # print(self.points_x[:self.pointNum])
            if self.drawPointFlag:
                for row in range(self.pointNum):
                    c = np.array([self.points_x[row], self.points_y[row]]).astype(np.int32)
                    r = self.points_z[row].astype(np.int32)
                    cv2.circle(
                        self.showImg, c, r, (255, 0, 0), 2
                    )
                cv2.putText(self.showImg, str(self.pointNum), (10, 40), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.5, (255, 255, 255))
            # print(num.value)
            time.sleep(0.03)

    def read(self): 
        return [self.running, self.showImg]

    def setExpose(self, expose):
        exposeValue = int(99 * (expose + 10) + 10)
        self.SDKdll.setValue(1, exposeValue)
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