import socket
import numpy as np
import cv2
import threading
import struct
import time

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
        self.sendTh = threading.Thread(target=self.send, daemon=True)
        self.sendTh.start()
        self.recvSock.bind(('', self.port))
    
    def send(self):
        count = 1
        while self.isRun:
            sendBuff = [0xa5, 0x5a, count & 0xff, (count & 0xff00)>>8, 0x47,0x52,0x59,0x50,0x49,0x43]
            self.sendSock.sendto(bytes(sendBuff), (self.ip, self.port))
            count = count + 1
            time.sleep(0.5)

    def recv(self):
        count = 1
        error_count = 0
        errorMax = 1024
        image = np.zeros(self.imgSize, dtype=np.uint8)
        count = count + 1
        while self.isRun:
            buff = b''
            try:
                buff = self.recvSock.recv(self.__BUFF_LEN)
            except socket.timeout:
                print('timeout')
                continue
            if (len(buff) < 4):
                continue
            packHeader = struct.unpack('H', buff[0:2])[0]
            packLen = struct.unpack('H', buff[2:4])[0] - 8
            if packHeader != 0x3c5a:
                # print('packHeader: ', end='')
                # print(buff[0:2].hex())
                continue
            if len(buff) < 1032:
                print('len: ', end='')
                print(buff.hex())
                continue
            error_count = 0
            packLine = struct.unpack('H', buff[4:6])[0]
            if packLine >= image.shape[0]:
                print('packLine: ', end='')
                print(packLine)
                break
            packIndex = int(buff[6])
            isLastPack = (int(buff[7]) == 1)
            image[packLine, packLen * packIndex : packLen * (packIndex + 1)] = np.array(list(buff[8:8+packLen])).astype(np.uint8)
            if isLastPack:
                self.recvImg = np.copy(image)
                continue
        
        # print('pack')
        time.sleep(0.01)
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
        