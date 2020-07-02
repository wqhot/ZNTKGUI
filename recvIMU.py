# -*- coding: utf-8 -*-
import sys
import serial
import threading
import queue
import struct
import math
import base64
import csv
import copy
import time


class RecvIMU():
    __HEAD1 = 0
    __HEAD2 = 1
    __LENGTH = 2
    __FREAM_ID = 3
    __FREQ = 4
    __AMP = 8
    __GYR_OUT = 12
    __ORTHOGONAL = 16
    __FRAME_CNT = 20
    __CRC_SUM = 21
    __BUF_LENGTH = 22

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
        headers = ['stamp', 'freq', 'amp', 'gyr', 'orthogonal']
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
                            r["freq"],
                            r["amp"],
                            r["gyr"],
                            r["ortgnl"]]
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
            headIndex = buffArray.find(bytearray(b'\x90\xeb'))
            if headIndex != -1:
                remainLength = remainLength - headIndex
                buffList = []
                buffList.extend(list(buffArray)[headIndex:])
                if len(buffList) > self.__BUF_LENGTH:
                    buffList = []
            else:  # 无帧头时
                buffList.extend(list(buffArray))
                remainLength = self.__BUF_LENGTH
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
                    freq = ((buffList[self.__FREQ + 0] << 24) +
                            (buffList[self.__FREQ + 1] << 16) +
                            (buffList[self.__FREQ + 2] << 8) +
                            (buffList[self.__FREQ + 3] << 0))
                    amp = ((buffList[self.__AMP + 0] << 24) +
                            (buffList[self.__AMP + 1] << 16) +
                            (buffList[self.__AMP + 2] << 8) +
                            (buffList[self.__AMP + 3] << 0))
                    gyr = ((buffList[self.__GYR_OUT + 0] << 24) +
                            (buffList[self.__GYR_OUT + 1] << 16) +
                            (buffList[self.__GYR_OUT + 2] << 8) +
                            (buffList[self.__GYR_OUT + 3] << 0))
                    ortgnl = ((buffList[self.__ORTHOGONAL + 0] << 24) +
                            (buffList[self.__ORTHOGONAL + 1] << 16) +
                            (buffList[self.__ORTHOGONAL + 2] << 8) +
                            (buffList[self.__ORTHOGONAL + 3] << 0))
                    dc["stamp"] = float(time.time())
                    dc["freq"] = freq
                    dc["amp"] = amp
                    dc["gyr"] = gyr
                    dc["ortgnl"] = ortgnl
                    if self.cond.acquire():
                        if (self.isRecv):
                            self.que.put(dc)
                        self.cond.notify_all()
                        self.cond.release()
                    
