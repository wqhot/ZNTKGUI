# -*- coding: utf-8 -*-
import sys
import socket
import threading
import queue
import struct
import math
import base64
import cv2
import numpy as np


class RecvData():
    __POSE_BY_CAM = 4
    __ANGLE_BY_CAM = 16
    __DT_BY_CAM = 32
    __POSE_BY_UPDATE = 40
    __ANGLE_BY_UPDATE = 52
    __DT_BY_UPDATE = 68
    __POSE_BY_PRE = 76
    __ANGLE_BY_PRE = 88
    __DT_BY_PRE = 104
    __DT_OF_FRAME = 112
    __THRESOLD = 120
    __COST_OF_IMG = 124
    __LENGTH = 133

    def __init__(self):
        self.mutex = threading.Lock()
        self.img_mutex = threading.Lock()
        self.que = queue.Queue(1024)
        self.img_que = queue.Queue(8)
        self.cond = threading.Condition()
        self.img_cond = threading.Condition()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 5577))
        self.sock_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_2.bind(("0.0.0.0", 5578))
        self.sock_2.listen()
        self.isrun = True
        self.issend = True
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.run_img, daemon=True)
        self.th_2.start()

    def pause(self):
        self.cond.acquire()
        # print("get cond")
        self.img_cond.acquire()
        # print("get img_cond")
        self.cond.release()
        self.img_cond.release()
        self.issend = False
    
    def stop(self):
        # self.sock.close()
        self.cond.acquire()
        # print("get cond")
        self.img_cond.acquire()
        # print("get img_cond")
        self.cond.release()
        self.img_cond.release()
        self.isrun = False

    def reconnect(self):
        self.cond.acquire()
        self.img_cond.acquire()
        self.cond.release()
        self.img_cond.release()
        self.isrun = False
        self.th.join()
        self.th_2.join()
        self.isrun = True
        self.issend = True
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.run_img, daemon=True)
        self.th_2.start()


    def start(self):
        self.issend = True
        # self.th = threading.Thread(target=self.run, daemon=True)
        # self.th.start()
        # self.th_2 = threading.Thread(target=self.run_img, daemon=True)
        # self.th_2.start()

    def isRun(self):
        return self.isrun

    def getImage(self):
        self.img_cond.acquire()
        self.img_cond.wait(0.5)
        img = None
        if not self.img_que.empty():
            r = self.img_que.get()
            img = np.asarray(bytearray(r), dtype='uint8')
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            # print("getImage")
        self.img_cond.notify_all()
        self.img_cond.release()
        return img

    def getData(self):
        r = None
        self.cond.acquire()
        self.cond.wait(0.5)
        if not self.que.empty():
            r = self.que.get()
            # print("getData")
        self.cond.release()
        return r

    def qua2eul(self, qua):
        w = float(qua[3])
        x = float(qua[0])
        y = float(qua[1])
        z = float(qua[2])

        r = math.atan2(2*(w*x+y*z), 1-2*(x*x+y*y))
        p = math.asin(2*(w*y-z*x))
        y = math.atan2(2*(w*z+x*y), 1-2*(z*z+y*y))

        angleR = r*180/math.pi
        angleP = p*180/math.pi
        angleY = y*180/math.pi
        eul = [angleP, angleY, angleR]

        return eul

    def run_img(self):
        while self.isrun:
            c_socket, c_address = self.sock_2.accept()
            while self.isrun:
                head = c_socket.recv(4)
                data = bytearray(head)
                if data.find(bytearray(b'\xff\xff\xff\xff')) != -1:
                    continue
                length = int.from_bytes(data, byteorder='little')
                if length == 0:
                    break
                # print(length)
                curSize = 0
                allData = b''
                while curSize < length:
                    remain = 1024 if (
                        length - curSize) > 1024 else (length - curSize)
                    data = c_socket.recv(remain)
                    remain = len(data)
                    index = data.rfind(bytearray(b'\xff'))
                    if index != -1:
                        if index == remain - 1:  # 刚好结束
                            break
                        elif remain - index < 5:  # 不足以接收长度
                            data1 = bytearray(data[index + 1:])
                            data2 = bytearray(
                                c_socket.recv(5 + index - remain))
                            data1.append(data2)
                            length = int.from_bytes(data1, byteorder='little')
                            curSize = 0
                            allData = b''
                            continue
                        else:  # 足够接收长度或剩余有数据
                            length = int.from_bytes(
                                bytearray(data[index + 1:index + 4]), byteorder='little')
                            curSize = 0
                            data1 = data[index + 5:]
                            allData = b''
                            allData += data1
                            curSize = curSize + len(data1)
                            continue
                    else:
                        allData += data
                        curSize = curSize + len(data)

                imgDecode = base64.b64decode(bytearray(allData))
                # print("start put que")
                if self.img_cond.acquire(timeout=0.5):
                    if self.img_que.full():
                        self.img_que.get_nowait()
                    if self.issend:
                        self.img_que.put(imgDecode)
                    self.img_cond.notify_all()
                    self.img_cond.release()
                # print("end put que")
                # if self.img_mutex.acquire():
                #     # print('img len %s'%len(allData))
                #     self.img_que.put(imgDecode)
                #     self.img_mutex.release()
            c_socket.close()

    def run(self):
        while self.isrun:
            data = []
            while len(data) < self.__LENGTH:
                buff = self.sock.recv(self.__LENGTH)
                buffArray = bytearray(buff)
                buffList = list(buffArray)
                index = buffArray.find(bytearray(b'\xff\xff\xff'))
                if index != -1:
                    data = []
                    buffList = buffList[index:]
                data.extend(buffList)
            # 收齐一帧
            sumcheck = sum(data[:-1]) % 256
            if sumcheck != data[-1]:
                print("sumcheck error!")
                break
            dc = {}

            dc["POSE_BY_CAM"] = [0.0, 0.0, 0.0]
            dc["POSE_BY_CAM"][0] = struct.unpack('f', bytes(
                data[self.__POSE_BY_CAM + 0:self.__POSE_BY_CAM + 4]))[0]
            dc["POSE_BY_CAM"][1] = struct.unpack('f', bytes(
                data[self.__POSE_BY_CAM + 4:self.__POSE_BY_CAM + 8]))[0]
            dc["POSE_BY_CAM"][2] = struct.unpack('f', bytes(
                data[self.__POSE_BY_CAM + 8:self.__POSE_BY_CAM + 12]))[0]

            dc["ANGLE_BY_CAM"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_CAM"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_CAM + 0:self.__ANGLE_BY_CAM + 4]))[0]
            dc["ANGLE_BY_CAM"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_CAM + 4:self.__ANGLE_BY_CAM + 8]))[0]
            dc["ANGLE_BY_CAM"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_CAM + 8:self.__ANGLE_BY_CAM + 12]))[0]
            dc["ANGLE_BY_CAM"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_CAM + 12:self.__ANGLE_BY_CAM + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_CAM"])
            dc["EUL_BY_CAM_X"] = eul[0]
            dc["EUL_BY_CAM_Y"] = eul[1]
            dc["EUL_BY_CAM_Z"] = eul[2]

            dc["DT_BY_CAM"] = struct.unpack('d', bytes(
                data[self.__DT_BY_CAM:self.__DT_BY_CAM+8]))[0]

            dc["POSE_BY_UPDATE"] = [0.0, 0.0, 0.0]
            dc["POSE_BY_UPDATE"][0] = struct.unpack('f', bytes(
                data[self.__POSE_BY_UPDATE + 0:self.__POSE_BY_UPDATE + 4]))[0]
            dc["POSE_BY_UPDATE"][1] = struct.unpack('f', bytes(
                data[self.__POSE_BY_UPDATE + 4:self.__POSE_BY_UPDATE + 8]))[0]
            dc["POSE_BY_UPDATE"][2] = struct.unpack('f', bytes(
                data[self.__POSE_BY_UPDATE + 8:self.__POSE_BY_UPDATE + 12]))[0]

            dc["ANGLE_BY_UPDATE"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_UPDATE"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_UPDATE + 0:self.__ANGLE_BY_UPDATE + 4]))[0]
            dc["ANGLE_BY_UPDATE"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_UPDATE + 4:self.__ANGLE_BY_UPDATE + 8]))[0]
            dc["ANGLE_BY_UPDATE"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_UPDATE + 8:self.__ANGLE_BY_UPDATE + 12]))[0]
            dc["ANGLE_BY_UPDATE"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_UPDATE + 12:self.__ANGLE_BY_UPDATE + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_UPDATE"])
            dc["EUL_BY_UPDATE_X"] = eul[0]
            dc["EUL_BY_UPDATE_Y"] = eul[1]
            dc["EUL_BY_UPDATE_Z"] = eul[2]

            dc["DT_BY_UPDATE"] = struct.unpack('d', bytes(
                data[self.__DT_BY_UPDATE:self.__DT_BY_UPDATE+8]))[0]

            dc["POSE_BY_PRE"] = [0.0, 0.0, 0.0]
            dc["POSE_BY_PRE"][0] = struct.unpack('f', bytes(
                data[self.__POSE_BY_PRE + 0:self.__POSE_BY_PRE + 4]))[0]
            dc["POSE_BY_PRE"][1] = struct.unpack('f', bytes(
                data[self.__POSE_BY_PRE + 4:self.__POSE_BY_PRE + 8]))[0]
            dc["POSE_BY_PRE"][2] = struct.unpack('f', bytes(
                data[self.__POSE_BY_PRE + 8:self.__POSE_BY_PRE + 12]))[0]

            dc["ANGLE_BY_PRE"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_PRE"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_PRE + 0:self.__ANGLE_BY_PRE + 4]))[0]
            dc["ANGLE_BY_PRE"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_PRE + 4:self.__ANGLE_BY_PRE + 8]))[0]
            dc["ANGLE_BY_PRE"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_PRE + 8:self.__ANGLE_BY_PRE + 12]))[0]
            dc["ANGLE_BY_PRE"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_PRE + 12:self.__ANGLE_BY_PRE + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_PRE"])
            dc["EUL_BY_PRE_X"] = eul[0]
            dc["EUL_BY_PRE_Y"] = eul[1]
            dc["EUL_BY_PRE_Z"] = eul[2]

            dc["DT_BY_PRE"] = struct.unpack('d', bytes(
                data[self.__DT_BY_PRE:self.__DT_BY_PRE+8]))[0]

            dc["DT_OF_FRAME"] = struct.unpack('d', bytes(
                data[self.__DT_OF_FRAME:self.__DT_OF_FRAME+8]))[0]

            dc["THRESOLD"] = struct.unpack('i', bytes(
                data[self.__THRESOLD:self.__THRESOLD+4]))[0]

            dc["COST_OF_IMG"] = struct.unpack('d', bytes(
                data[self.__COST_OF_IMG:self.__COST_OF_IMG+8]))[0]

            self.cond.acquire()
            if (self.issend):
                self.que.put(dc)
            self.cond.notify_all()
            self.cond.release()
            # if self.mutex.acquire():
            #     self.que.put(dc)
            #     self.mutex.release()
        self.sock.close()
