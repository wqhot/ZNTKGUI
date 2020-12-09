# -*- coding: utf-8 -*-
import sys
import socket
import threading
import queue
import struct
import math
import base64
import csv
import copy
import time
import numpy as np
import cv2


class recvAR():

    __BUFF_LEN = 65540
    __PACK_SIZE = 4096
    __GROUP_IP_ADDRESS = "224.0.0.100"
    __NIC_NAME = "wlp2s0"
    def __init__(self):
        self.cond = threading.Condition()
        self.isrun = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.bind((self.__GROUP_IP_ADDRESS, 10001))
        self.sock.bind(("0.0.0.0", 10001))

    def start(self):
        self.th = threading.Thread(target=self.__recv_img_thread, daemon=True)
        self.th.start()

    def __recv_img_thread(self):
        while (self.isrun):
            # 接受长度头
            buff = b''
            while (len(buff) != 4) and self.isrun:
                buff = self.sock.recv(self.__BUFF_LEN)
            total_length = struct.unpack('i', buff)[0]
            total_pack = int(1 + (total_length - 1) / self.__PACK_SIZE)
            image_buff = b''
            recv_length = 0
            for i in range(total_pack):
                buff = self.sock.recv(self.__BUFF_LEN)
                image_buff = image_buff + buff
                recv_length = recv_length + len(buff)
            if recv_length != total_length:
                print("Received unexpected size pack: {1}, except {2}".format(
                    recv_length, total_length))
                continue
            else:
                raw_data = np.array(list(bytearray(image_buff)), dtype=np.int8)
                image = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
                cv2.imshow("aaa", image)
                cv2.waitKey(1)

    def __recv_detect_thread(self):
        while(self.isrun):
            pass


if __name__ == "__main__":
    recv = recvAR()
    recv.start()
    while True:
        time.sleep(1)
