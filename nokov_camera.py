import socket
import numpy as np
import cv2
import threading
import struct

class NOKOVCamera():
    streamSource = None
    camera = None
    ip = ""
    port = 6553
    __BUFF_LEN = 1500
    def  __init__(self, index):
        self.ip = "10.1.1." + str(index)
        self.sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSock.settimeout(0.5)
        self.isRun = True
        self.running = True
        self.imgSize = (1024,2048)
        self.recvImg = np.zeros(self.imgSize, dtype=np.uint8)
        self.recvTh = threading.Thread(target=self.recv, daemon=True)
        self.recvTh.start()
        self.recvSock.bind(('', self.port))
        
    def recv(self):
        count = 1
        while self.isRun:
            sendBuff = [0xa5, 0x5a, count & 0xff, (count & 0xff00)>>8, 0x47,0x52,0x59,0x50,0x49,0x43]
            self.sendSock.sendto(bytes(sendBuff), (self.ip, self.port))
            image = np.zeros(self.imgSize, dtype=np.uint8)
            count = count + 1
            while self.isRun:
                buff = b''
                try:
                    buff = self.recvSock.recv(self.__BUFF_LEN)
                except socket.timeout:
                    # print('timeout')
                    break
                if len(buff) < 1032:
                    continue
                packHeader = struct.unpack('H', buff[0:2])[0]
                packLen = struct.unpack('H', buff[2:4])[0]
                if packHeader != 0x3c5a:
                    continue
                packLine = struct.unpack('H', buff[4:6])[0] - 1
                if packLine >= image.shape[0]:
                    continue
                packIndex = int(buff[7])
                isLastPack = (int(buff[6]) == 1)
                image[packLine, packLen * packIndex : packLen * (packIndex + 1)] = np.array(list(buff[8:8+packLen])).astype(np.uint8)
                if isLastPack:
                    self.recvImg = np.copy(image)
                    break
        self.recvSock.close()
        self.sendSock.close()
        self.running = False
        print('Nokov Release')

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
        self.isRun = False
        