# -*- coding: utf-8 -*-
import sys
import serial
import threading
import queue
import struct
import math
import base64
import cv2
import csv
import copy
import time
import numpy as np


class RecvIMU():
    __HEAD1 = 0
    __HEAD2 = 1
    __X_ANG = 2
    __Z_ANG = 5
    __BUF_LENGTH = 11

    def __init__(self, portName):
        # self.recvTh
        self.isRecv = True
        self.que = queue.Queue(maxsize=1024)
        self.cond = threading.Condition()
        self.serial = serial.Serial(
            port=portName, baudrate=230400, timeout=0.5)
        self.th = threading.Thread(target=self.recv, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.save, daemon=True)
        self.th_2.start()

    def save(self):
        headers = ['stamp', 'x_ang', 'z_ang']
        csv_name = './history/' + \
            str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())) + '_imu.csv'
        with open(csv_name, 'w') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            while self.isRecv:
                r = None
                if self.cond.acquire():
                    if self.que.empty():
                        self.cond.wait(0.5)
                    if not self.que.empty():
                        r = self.que.get()
                        # print("getData")
                    self.cond.release()
                if r is not None:
                    line = [r["stamp"],
                            r["x_ang"],
                            r["z_ang"]]
                    f_csv.writerow(line)

    def recv(self):
        remainLength = self.__BUF_LENGTH
        buffList = []
        while self.isRecv:
            buff = self.serial.read(remainLength)
            if len(buff) != remainLength:
                break
            buffArray = bytearray(buff)
            # 找帧头
            headIndex = buffArray.find(bytearray(b'\x55\xff'))
            if headIndex != -1:
                remainLength = remainLength - headIndex
                buffList = []
                buffList.extend(list(buffArray)[headIndex:])
            else:  # 无帧头时
                buffList.extend(list(buffArray))
                remainLength = self.__BUF_LENGTH
                if len(buffList) > self.__BUF_LENGTH:
                    buffList = []
            if remainLength == 0:
                remainLength = self.__BUF_LENGTH

            # 收齐数据
            if len(buffList) == self.__BUF_LENGTH:
                # check sum
                sum = 0
                for bt in buffList[:-1]:
                    sum = (sum + bt) % 256
                if sum == buffList[-1]:
                    dc = {}
                    # hardcode...
                    x_ang = ((buffList[self.__X_ANG + 2] << 16) if buffList[self.__X_ANG + 2] < 0x7f else ((buffList[self.__X_ANG + 2] - 0xff) << 16) +
                            (buffList[self.__X_ANG + 1] << 8) +
                            (buffList[self.__X_ANG + 0] << 0)) * 0.0001
                    z_ang = ((buffList[self.__Z_ANG + 2] << 16) if buffList[self.__Z_ANG + 2] < 0x7f else ((buffList[self.__Z_ANG + 2] - 0xff) << 16) +
                            (buffList[self.__Z_ANG + 1] << 8) +
                            (buffList[self.__Z_ANG + 0] << 0)) * 0.0001
                    dc["stamp"] = float(time.time())
                    dc["x_ang"] = x_ang
                    dc["z_ang"] = z_ang
                    print(dc)
                    if self.cond.acquire():
                        if (self.isRecv):
                            self.que.put(dc)
                        self.cond.notify_all()
                        self.cond.release()
                    
