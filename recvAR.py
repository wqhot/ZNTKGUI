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
from PIL import Image,ImageDraw,ImageFont

class recvAR():

    __BUFF_LEN = 65540
    __PACK_SIZE = 4096
    __IMAGE_FINAL_ROWS = 1080
    __IMAGE_FINAL_COLS = 1920
    __GROUP_IP_ADDRESS = "224.0.0.100"
    __NIC_NAME = "wlp2s0"
    def __init__(self):
        self.cond = threading.Condition()
        self.isrun = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.bind((self.__GROUP_IP_ADDRESS, 10001))
        self.sock.bind(("0.0.0.0", 10005))
        # status = self.sock.setsockopt(socket.IPPROTO_IP,
        #                 socket.IP_ADD_MEMBERSHIP,
        #                 socket.inet_aton(self.__GROUP_IP_ADDRESS) + socket.inet_aton("0.0.0.0"))

    def start(self):
        self.th = threading.Thread(target=self.__recv_img_thread, daemon=True)
        self.th.start()

    def __recv_img_thread(self):
        font = ImageFont.truetype('./res/simkai.ttf', 70)
        while (self.isrun):
            # 接受长度头
            buff = b''
            while (len(buff) != 4) and self.isrun:
                buff = self.sock.recv(self.__BUFF_LEN)
            total_length = struct.unpack('i', buff)[0]
            print("total_length = " + str(total_length))
            total_pack = int(1 + (total_length - 1) / self.__PACK_SIZE)
            image_buff = b''
            recv_length = 0
            for i in range(total_pack):
                buff = self.sock.recv(self.__BUFF_LEN)
                image_buff = image_buff + buff
                recv_length = recv_length + len(buff)
            if recv_length != total_length:
                print("Received unexpected size pack: {0}, except {1}".format(
                    recv_length, total_length))
                continue
            else:
                raw_data = np.array(list(bytearray(image_buff)), dtype=np.int8)
                try:
                    image = cv2.imdecode(raw_data, cv2.IMREAD_UNCHANGED)
                    image_extend = cv2.copyMakeBorder(
                        image, 
                        180,
                        180,
                        0,
                        0,
                        cv2.BORDER_CONSTANT, value=[0,0,0])               
                    img_PIL = Image.fromarray(image_extend)
                    position = (450, 90)
                    str_zh = '兵器计算所智能头盔随动观察'
                    draw = ImageDraw.Draw(img_PIL)
                    draw.text(position, str_zh, font=font, fill=(255, 255, 255))
                    img_OpenCV = np.asarray(img_PIL)
                    # print("image : " + str(image_extend.shape))
                    cv2.imshow("aaa", img_OpenCV)
                    cv2.waitKey(1)
                except:
                    print("fffff")
                    continue
                

    def __recv_detect_thread(self):
        while(self.isrun):
            pass


if __name__ == "__main__":
    recv = recvAR()
    recv.start()
    while True:
        time.sleep(1)