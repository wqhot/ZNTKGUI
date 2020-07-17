# -*- coding: utf-8 -*-
import sys
import serial
import threading
import socket
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
    __X_ANG = 2
    __Z_ANG = 6
    __STAMP = 10
    __BUF_LENGTH = 19

    def __init__(self, usesock=False, port=None, socketPort=5580, saveName='', portName='',dir_name='./history/', event=None, save=True):
        # self.recvTh
        self.isRecv = True
        self.isSave = save
        self.pause = True
        self.saveName = saveName
        self.que = queue.Queue(maxsize=1024)
        self.cond = threading.Condition()
        self.dir_name = dir_name
        self.recvData = None
        self.usesock = usesock
        
        if self.usesock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", socketPort))
        else:
            self.sock = None
        if event is None:
            self.event = threading.Event()
        else:
            self.event = event
        if port is None and portName == '' and not self.usesock:
            return
        if port is not None:
            portName = port.device
        if not self.usesock:
            self.serial = serial.Serial(
                port=portName, baudrate=230400, timeout=0.5)
        self.th = threading.Thread(target=self.recv, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.save, daemon=True)
        self.th_2.start()
        

    def getIMUdata(self):
        if self.recvData is None:
            return None
        r = copy.deepcopy(self.recvData)
        self.recvData = None
        return r

    def save(self):
        headers = ['stamp', 'x_ang' + self.saveName, 'z_ang' + self.saveName]
        while self.isRecv:
            csv_name = './history/' + \
                str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '_imu' + self.saveName + '.csv'
            with open(csv_name, 'w') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(headers)
                while self.isSave:
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
                    if self.event.is_set():
                        print("创建新文件")
                        self.event.clear()
                        break

    def recv(self):
        remainLength = self.__BUF_LENGTH
        buffList = []
        while self.isRecv:
            if self.usesock:
                buff = self.sock.recv(remainLength)
            else:
                buff = self.serial.read(remainLength)
            if len(buff) == 0:
                continue           
            remainLength = len(buff)
            buffArray = bytearray(buff)
            # 找帧头
            headIndex = buffArray.find(bytearray(b'\x55\xff'))
            if headIndex != -1:
                remainLength = self.__BUF_LENGTH - (remainLength - headIndex)
                buffList = []
                buffList.extend(list(buffArray)[headIndex:])
            else:  # 无帧头时
                buffList.extend(list(buffArray))
                remainLength = self.__BUF_LENGTH
                print("head not fount")
                if len(buffList) > self.__BUF_LENGTH:
                    buffList = []
                    print("drop")
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
                    x_ang = struct.unpack('f', bytes(
                            buffList[self.__X_ANG:self.__X_ANG+4]))[0]
                    z_ang = struct.unpack('f', bytes(
                            buffList[self.__Z_ANG:self.__Z_ANG+4]))[0]
                    stamp = struct.unpack('d', bytes(
                            buffList[self.__STAMP:self.__STAMP+8]))[0]
                    dc["stamp"] = stamp
                    dc["x_ang"] = x_ang
                    dc["z_ang"] = z_ang
                    # print(buffList[self.__Z_ANG:self.__Z_ANG+4], end='')
                    # print(" " + str(dc["z_ang"]))
                    if not self.pause:
                        self.recvData = dc
                    if self.cond.acquire():
                        if (self.isRecv and self.isSave and not self.pause):
                            self.que.put(dc)
                            self.cond.notify_all()
                        self.cond.release()
                else:
                    print("checkerror")
                buffList = []
                    
