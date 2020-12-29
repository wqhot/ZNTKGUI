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
# import cv2

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
    __COST_OF_PRE = 132
    __COST_OF_UPDT = 140
    __STAMP = 148
    __ANGLE_BY_IMU = 156
    __LENGTH = 197
    __OLDLENGTH = 173
    __IMAGE_FEATURE_POINT_X = 172
    __IMAGE_FEATURE_POINT_Y = 176

    def __init__(self, enable_save=True):
        self.mutex = threading.Lock()
        # self.img_mutex = threading.Lock()
        self.que = queue.Queue(1024)
        # self.img_que = queue.Queue(8)
        self.cond = threading.Condition()
        # self.img_cond = threading.Condition()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 5577))
        # self.sock_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock_2.bind(("0.0.0.0", 5578))
        # self.sock_2.listen()
        self.isrun = True
        self.issave = enable_save
        self.issend = True
        self.displayDict = None
        self.contsum = 0
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.save, daemon=True)
        self.th_2.start()

    def pause(self):
        # self.cond.acquire()
        # print("get cond")
        # self.img_cond.acquire()
        # print("get img_cond")
        # self.cond.release()
        # self.img_cond.release()
        self.issend = False

    def stop(self):
        # self.sock.close()
        self.cond.acquire()
        # print("get cond")
        # self.img_cond.acquire()
        # print("get img_cond")
        # self.img_cond.release()
        self.isrun = False
        self.issave = False
        self.cond.release()

    def reconnect(self):
        self.cond.acquire()
        # self.img_cond.acquire()
        self.cond.release()
        # self.img_cond.release()
        self.isrun = False
        self.th.join()
        # self.th_2.join()
        self.isrun = True
        self.issend = True
        self.th = threading.Thread(target=self.run, daemon=True)
        self.th.start()
        self.th_2 = threading.Thread(target=self.save, daemon=True)
        self.th_2.start()

    def start(self):
        self.issend = True
        # self.th = threading.Thread(target=self.run, daemon=True)
        # self.th.start()
        # self.th_2 = threading.Thread(target=self.run_img, daemon=True)
        # self.th_2.start()

    def isRun(self):
        return self.isrun

    # def getImage(self):
    #     self.img_cond.acquire()
    #     self.img_cond.wait(0.5)
    #     img = None
    #     if not self.img_que.empty():
    #         r = self.img_que.get()
    #         img = np.asarray(bytearray(r), dtype='uint8')
    #         img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    #         # print("getImage")
    #     self.img_cond.notify_all()
    #     self.img_cond.release()
    #     return img

    def getData(self):
        if self.displayDict is None:
            return None
        r = copy.deepcopy(self.displayDict)
        self.displayDict = None
        return r

    def qua2eul(self, qua):
        w = float(qua[3])
        x = float(qua[0])
        y = float(qua[1])
        z = float(qua[2])
        epsilon = 0.001953125
        threshold = 1.0 - epsilon
        r11 = 2.0 * (x * y + z * w)
        r12 = w * w + x * x - y * y - z * z
        r21 = -2.0 * (x * z - y * w)
        r31 = 2.0 * (y * z + x * w)
        r32 = w * w - x * x - y * y + z * z
        eul = [0.0, 0.0, 0.0]
        if r21 < -threshold or r21 > threshold:
            sign = 1 if r21 > 0 else -1
            eul[0] = 0
            eul[1] = sign * math.pi / 2.0 * 180.0 / math.pi
            eul[2] = -2 * sign * math.atan2(x, z) * 180.0 / math.pi
        else:
            eul[0] = math.atan2(r31, r32) * 180.0 / math.pi
            eul[1] = math.asin(r21) * 180.0 / math.pi
            eul[2] = math.atan2(r11, r12) * 180.0 / math.pi
        return eul

    def close_start(self):
        self.issave = False
        self.issend = False
        self.th_2.join()
        self.contsum = 0
        self.issend = True
        self.issave = True
        self.th_2 = threading.Thread(target=self.save, daemon=True)
        self.th_2.start()

    def save(self):
        headers = ['stamp', 'eul_x', 'eul_y', 'eul_z', 't_x', 't_y', 't_z',
                   'cam_x', 'cam_y', 'cam_z', 'updt_x', 'updt_y', 'updt_z',
                   'imu_x', 'imu_y', 'imu_z', 'cost_of_eul', 'cost_of_cam', 'cost_of_update']
        csv_name = './history/' + \
            str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.csv'
        with open(csv_name, 'w') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)
            while self.issave:
                r = None
                if self.cond.acquire():
                    if self.que.empty():
                        self.cond.wait(0.5)
                    if not self.que.empty():
                        r = self.que.get()
                        # print("getData")
                    self.cond.release()
                if r is not None:
                    line = [r["STAMP"],
                            r["EUL_BY_PRE_X"],
                            r["EUL_BY_PRE_Y"],
                            r["EUL_BY_PRE_Z"],
                            r["POSE_BY_PRE"][0],
                            r["POSE_BY_PRE"][1],
                            r["POSE_BY_PRE"][2],
                            r["EUL_BY_CAM_X"],
                            r["EUL_BY_CAM_Y"],
                            r["EUL_BY_CAM_Z"],
                            r["EUL_BY_UPDATE_X"],
                            r["EUL_BY_UPDATE_Y"],
                            r["EUL_BY_UPDATE_Z"],
                            r["EUL_BY_IMU_X"],
                            r["EUL_BY_IMU_Y"],
                            r["EUL_BY_IMU_Z"],
                            r["COST_OF_PRE"],
                            r["COST_OF_IMG"],
                            r["COST_OF_UPDT"]]
                    f_csv.writerow(line)

    def run(self):
        count = 0
        while self.isrun:
            data = []
            while len(data) < self.__LENGTH:
                # remain = self.__LENGTH - len(data)
                buff = self.sock.recv(1024)
                buffArray = bytearray(buff)
                buffList = list(buffArray)
                index = buffArray.find(bytearray(b'\xff\xff\xff'))
                if index != -1:
                    data = []
                    buffList = buffList[index:]
                    # print(time.time())
                    self.__LENGTH = buffList[index + 3]
                    # print(self.__LENGTH)
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

            dc["COST_OF_PRE"] = struct.unpack('d', bytes(
                data[self.__COST_OF_PRE:self.__COST_OF_PRE+8]))[0]

            dc["COST_OF_UPDT"] = struct.unpack('d', bytes(
                data[self.__COST_OF_UPDT:self.__COST_OF_UPDT+8]))[0] 

            # dc["STAMP"] = float(time.time())
            dc["STAMP"] = struct.unpack('d', bytes(
                data[self.__STAMP:self.__STAMP+8]))[0]

            dc["ANGLE_BY_IMU"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_IMU"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_IMU + 0:self.__ANGLE_BY_IMU + 4]))[0]
            dc["ANGLE_BY_IMU"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_IMU + 4:self.__ANGLE_BY_IMU + 8]))[0]
            dc["ANGLE_BY_IMU"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_IMU + 8:self.__ANGLE_BY_IMU + 12]))[0]
            dc["ANGLE_BY_IMU"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_IMU + 12:self.__ANGLE_BY_IMU + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_IMU"])
            dc["EUL_BY_IMU_X"] = eul[0]
            dc["EUL_BY_IMU_Y"] = eul[1]
            dc["EUL_BY_IMU_Z"] = eul[2]

            pts = int((self.__LENGTH - self.__OLDLENGTH) / 8)
            ptx = []
            pty = []
            for i in range(pts):
                ptx.append(struct.unpack('f', bytes(
                    data[self.__IMAGE_FEATURE_POINT_X + 8 * i: self.__IMAGE_FEATURE_POINT_X + 4 + 8 * i]))[0])
                pty.append(struct.unpack('f', bytes(
                    data[self.__IMAGE_FEATURE_POINT_Y + 8 * i: self.__IMAGE_FEATURE_POINT_Y + 4 + 8 * i]))[0])

            dc["IMAGE_FEATURE_POINT_X"] = ptx
            dc["IMAGE_FEATURE_POINT_Y"] = pty
            save_dc = {}
            save_dc["EUL_BY_PRE_X"] = dc["EUL_BY_PRE_X"]
            save_dc["EUL_BY_PRE_Y"] = dc["EUL_BY_PRE_Y"]
            save_dc["EUL_BY_PRE_Z"] = dc["EUL_BY_PRE_Z"]

            save_dc["EUL_BY_CAM_X"] = dc["EUL_BY_CAM_X"]
            save_dc["EUL_BY_CAM_Y"] = dc["EUL_BY_CAM_Y"]
            save_dc["EUL_BY_CAM_Z"] = dc["EUL_BY_CAM_Z"]

            save_dc["EUL_BY_UPDATE_X"] = dc["EUL_BY_UPDATE_X"]
            save_dc["EUL_BY_UPDATE_Y"] = dc["EUL_BY_UPDATE_Y"]
            save_dc["EUL_BY_UPDATE_Z"] = dc["EUL_BY_UPDATE_Z"]

            save_dc["EUL_BY_IMU_X"] = dc["EUL_BY_IMU_X"]
            save_dc["EUL_BY_IMU_Y"] = dc["EUL_BY_IMU_Y"]
            save_dc["EUL_BY_IMU_Z"] = dc["EUL_BY_IMU_Z"]

            save_dc["POSE_BY_PRE"] = dc["POSE_BY_PRE"]
            save_dc["STAMP"] = dc["STAMP"]

            save_dc["COST_OF_IMG"] = dc["COST_OF_IMG"]
            save_dc["COST_OF_PRE"] = dc["COST_OF_PRE"]
            save_dc["COST_OF_UPDT"] = dc["COST_OF_UPDT"]

            self.contsum = self.contsum + 1
            if (self.issend):
                self.displayDict = dc
            if self.cond.acquire():
                if (self.issave):
                    self.que.put(save_dc)
                self.cond.notify_all()
                self.cond.release()
            count = (count + 1) % 200
            # print("finish")
            # if self.mutex.acquire():
            #     self.que.put(dc)
            #     self.mutex.release()
        self.sock.close()

if __name__ == '__main__':
    recv = RecvData()
    while True:
        time.sleep(0.01)
