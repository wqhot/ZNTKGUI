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
from scipy.spatial.transform import Rotation
import numpy as np
# import cv2

class RecvData():
    __POSE_BY_CAM = 5
    __ANGLE_BY_CAM = 17
    __DT_BY_CAM = 33
    __POSE_BY_UPDATE = 41
    __ANGLE_BY_UPDATE = 53
    __DT_BY_UPDATE = 69
    __POSE_BY_PRE = 77
    __ANGLE_BY_PRE = 89
    __DT_BY_PRE = 105
    __DT_OF_FRAME = 113
    __THRESOLD = 121
    __COST_OF_IMG = 125
    __COST_OF_PRE = 133
    __COST_OF_UPDT = 141
    __STAMP = 149
    __ANGLE_BY_IMU = 157
    __ANGLE_BY_INTEGRAL = 173
    __ANGLE_BY_STABLE = 189
    __ANGLE_VELOCITY = 201
    __OMEGA_WITH_CAM = 217
    __OMEGA_NO_CAM = 229
    __ACC_WITH_CAM = 241
    __ACC_NO_CAM = 253
    __ACC_REL = 265
    __LENGTH = 286
    __OLDLENGTH = 278
    __IMAGE_FEATURE_POINT_X = 277
    __IMAGE_FEATURE_POINT_Y = 281

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

    def transpose_qua(self, qua):
        qua = np.array(qua)
        if np.linalg.norm(qua) == 0:
            return qua
        R = Rotation.from_quat(qua).as_matrix()
        R = R.transpose()
        rot = Rotation.from_matrix(R)
        qua = rot.as_quat()
        return qua

    def qua2mat(self, qua):
        R = Rotation.from_quat(qua)
        # w = float(qua[3])
        # x = float(qua[0])
        # y = float(qua[1])
        # z = float(qua[2])
        # R = np.zeros(shape=(3,3))
        # R[0,0] = 1 - 2 * y * y -2 * z * z
        # R[0,1] = 2 * x * y + 2 * w * z
        # R[0,2] = 2 * x * z - 2 * w * y

        # R[1,0] = 2 * x * y - 2 * w * z
        # R[1,1] = 1 - 2 * x * x -2 * z * z
        # R[1,2] = 2 * y * z + 2 * w * x

        # R[2,0] = 2 * x * z + 2 * w * y
        # R[2,1] = 2 * y * z - 2 * w * x
        # R[2,2] = 1 - 2 * x * x -2 * y * y
        #R = R.transpose()
        return R

    def mat2qua(self, R):
        qua = [0, 0, 0, 0]
        w = float(qua[3])
        x = float(qua[0])
        y = float(qua[1])
        z = float(qua[2])
        R = np.zeros(shape=(3,3))
        R[0,0] = 1 - 2 * y * y -2 * z * z
        R[0,1] = 2 * x * y + 2 * w * z
        R[0,2] = 2 * x * z - 2 * w * y

        R[1,0] = 2 * x * y - 2 * w * z
        R[1,1] = 1 - 2 * x * x -2 * z * z
        R[1,2] = 2 * y * z + 2 * w * x

        R[2,0] = 2 * x * z + 2 * w * y
        R[2,1] = 2 * y * z - 2 * w * x
        R[2,2] = 1 - 2 * x * x -2 * y * y

        #R = R.transpose()
        return R


    def qua2eul(self, qua):
        if np.linalg.norm(qua) == 0:
            return [0,0,0]
        r = Rotation.from_quat(qua)
        return list(r.as_euler('XYZ', degrees=True))
        # qua = self.transpose_qua(qua)
        # w = float(qua[3])
        # x = float(qua[0])
        # y = float(qua[1])
        # z = float(qua[2])
        # epsilon = 0.001953125
        # threshold = 1.0 - epsilon
        # r11 = 2.0 * (x * y + z * w)
        # r12 = w * w + x * x - y * y - z * z
        # r21 = -2.0 * (x * z - y * w)
        # r31 = 2.0 * (y * z + x * w)
        # r32 = w * w - x * x - y * y + z * z
        # eul = [0.0, 0.0, 0.0]
        # if r21 < -threshold or r21 > threshold:
        #     sign = 1 if r21 > 0 else -1
        #     eul[0] = 0
        #     eul[1] = sign * math.pi / 2.0 * 180.0 / math.pi
        #     eul[2] = -2 * sign * math.atan2(x, z) * 180.0 / math.pi
        # else:
        #     eul[0] = math.atan2(r31, r32) * 180.0 / math.pi
        #     eul[1] = math.asin(r21) * 180.0 / math.pi
        #     eul[2] = math.atan2(r11, r12) * 180.0 / math.pi
        # return eul

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
                   'imu_x', 'imu_y', 'imu_z', 'omega_with_cam_x', 'omega_with_cam_y', 'omega_with_cam_z',
                   'omega_no_cam_x', 'omega_no_cam_y', 'omega_no_cam_z',
                   'omega_rel_x', 'omega_rel_y', 'omega_rel_z',
                   'cost_of_eul', 'cost_of_cam', 'cost_of_update',
                   'quat_pre_w', 'quat_pre_x', 'quat_pre_y', 'quat_pre_z',
                   'acc_with_cam_x', 'acc_with_cam_y', 'acc_with_cam_z',
                   'acc_no_cam_x', 'acc_no_cam_y', 'acc_no_cam_z',
                   'acc_rel_x', 'acc_rel_y', 'acc_rel_z']
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
                            r["OMEGA_WITH_CAM_X"],
                            r["OMEGA_WITH_CAM_Y"],
                            r["OMEGA_WITH_CAM_Z"],
                            r["OMEGA_NO_CAM_X"],
                            r["OMEGA_NO_CAM_Y"],
                            r["OMEGA_NO_CAM_Z"],
                            r["ANGLE_VELOCITY_X"],
                            r["ANGLE_VELOCITY_Y"],
                            r["ANGLE_VELOCITY_Z"],
                            r["COST_OF_PRE"],
                            r["COST_OF_IMG"],
                            r["COST_OF_UPDT"],
                            # 0,0,0,0]
                            r["ANGLE_BY_PRE"][3],
                            r["ANGLE_BY_PRE"][0],
                            r["ANGLE_BY_PRE"][1],
                            r["ANGLE_BY_PRE"][2],
                            r["ACC_WITH_CAM_X"],
                            r["ACC_WITH_CAM_Y"],
                            r["ACC_WITH_CAM_Z"],
                            r["ACC_NO_CAM_X"],
                            r["ACC_NO_CAM_Y"],
                            r["ACC_NO_CAM_Z"],
                            r["ACC_REL_CAM_X"],
                            r["ACC_REL_CAM_Y"],
                            r["ACC_REL_CAM_Z"]]
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
                    self.__LENGTH = buffList[index + 3] + buffList[index + 4] * 256
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

            dc["ANGLE_BY_INTEGRAL"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_INTEGRAL"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_INTEGRAL + 0:self.__ANGLE_BY_INTEGRAL + 4]))[0]
            dc["ANGLE_BY_INTEGRAL"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_INTEGRAL + 4:self.__ANGLE_BY_INTEGRAL + 8]))[0]
            dc["ANGLE_BY_INTEGRAL"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_INTEGRAL + 8:self.__ANGLE_BY_INTEGRAL + 12]))[0]
            dc["ANGLE_BY_INTEGRAL"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_INTEGRAL + 12:self.__ANGLE_BY_INTEGRAL + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_INTEGRAL"])
            dc["EUL_BY_INTEGRAL_X"] = eul[0]
            dc["EUL_BY_INTEGRAL_Y"] = eul[1]
            dc["EUL_BY_INTEGRAL_Z"] = eul[2]

            dc["ANGLE_BY_STABLE"] = [0.0, 0.0, 0.0, 0.0]
            dc["ANGLE_BY_STABLE"][0] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_STABLE + 0:self.__ANGLE_BY_STABLE + 4]))[0]
            dc["ANGLE_BY_STABLE"][1] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_STABLE + 4:self.__ANGLE_BY_STABLE + 8]))[0]
            dc["ANGLE_BY_STABLE"][2] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_STABLE + 8:self.__ANGLE_BY_STABLE + 12]))[0]
            dc["ANGLE_BY_STABLE"][3] = struct.unpack('f', bytes(
                data[self.__ANGLE_BY_STABLE + 12:self.__ANGLE_BY_STABLE + 16]))[0]

            eul = self.qua2eul(dc["ANGLE_BY_STABLE"])
            dc["EUL_BY_STABLE_X"] = eul[0]
            dc["EUL_BY_STABLE_Y"] = eul[1]
            dc["EUL_BY_STABLE_Z"] = eul[2]

            dc["ANGLE_VELOCITY_X"] = struct.unpack('f', bytes(
                data[self.__ANGLE_VELOCITY + 0:self.__ANGLE_VELOCITY + 4]))[0]
            dc["ANGLE_VELOCITY_Y"] = struct.unpack('f', bytes(
                data[self.__ANGLE_VELOCITY + 4:self.__ANGLE_VELOCITY + 8]))[0]
            dc["ANGLE_VELOCITY_Z"] = struct.unpack('f', bytes(
                data[self.__ANGLE_VELOCITY + 8:self.__ANGLE_VELOCITY + 12]))[0]

            dc["OMEGA_WITH_CAM_X"] = struct.unpack('f', bytes(
                data[self.__OMEGA_WITH_CAM + 0:self.__OMEGA_WITH_CAM + 4]))[0]
            dc["OMEGA_WITH_CAM_Y"] = struct.unpack('f', bytes(
                data[self.__OMEGA_WITH_CAM + 4:self.__OMEGA_WITH_CAM + 8]))[0]
            dc["OMEGA_WITH_CAM_Z"] = struct.unpack('f', bytes(
                data[self.__OMEGA_WITH_CAM + 8:self.__OMEGA_WITH_CAM + 12]))[0]

            dc["OMEGA_NO_CAM_X"] = struct.unpack('f', bytes(
                data[self.__OMEGA_NO_CAM + 0:self.__OMEGA_NO_CAM + 4]))[0]
            dc["OMEGA_NO_CAM_Y"] = struct.unpack('f', bytes(
                data[self.__OMEGA_NO_CAM + 4:self.__OMEGA_NO_CAM + 8]))[0]
            dc["OMEGA_NO_CAM_Z"] = struct.unpack('f', bytes(
                data[self.__OMEGA_NO_CAM + 8:self.__OMEGA_NO_CAM + 12]))[0]

            dc["ACC_WITH_CAM_X"] = struct.unpack('f', bytes(
                data[self.__ACC_WITH_CAM + 0:self.__ACC_WITH_CAM + 4]))[0]
            dc["ACC_WITH_CAM_Y"] = struct.unpack('f', bytes(
                data[self.__ACC_WITH_CAM + 4:self.__ACC_WITH_CAM + 8]))[0]
            dc["ACC_WITH_CAM_Z"] = struct.unpack('f', bytes(
                data[self.__ACC_WITH_CAM + 8:self.__ACC_WITH_CAM + 12]))[0]

            dc["ACC_NO_CAM_X"] = struct.unpack('f', bytes(
                data[self.__ACC_NO_CAM + 0:self.__ACC_NO_CAM + 4]))[0]
            dc["ACC_NO_CAM_Y"] = struct.unpack('f', bytes(
                data[self.__ACC_NO_CAM + 4:self.__ACC_NO_CAM + 8]))[0]
            dc["ACC_NO_CAM_Z"] = struct.unpack('f', bytes(
                data[self.__ACC_NO_CAM + 8:self.__ACC_NO_CAM + 12]))[0]

            dc["ACC_REL_CAM_X"] = struct.unpack('f', bytes(
                data[self.__ACC_REL + 0:self.__ACC_REL + 4]))[0]
            dc["ACC_REL_CAM_Y"] = struct.unpack('f', bytes(
                data[self.__ACC_REL + 4:self.__ACC_REL + 8]))[0]
            dc["ACC_REL_CAM_Z"] = struct.unpack('f', bytes(
                data[self.__ACC_REL + 8:self.__ACC_REL + 12]))[0]

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

            save_dc["ANGLE_VELOCITY_X"] = dc["ANGLE_VELOCITY_X"]
            save_dc["ANGLE_VELOCITY_Y"] = dc["ANGLE_VELOCITY_Y"]
            save_dc["ANGLE_VELOCITY_Z"] = dc["ANGLE_VELOCITY_Z"]

            save_dc["OMEGA_WITH_CAM_X"] = dc["OMEGA_WITH_CAM_X"]
            save_dc["OMEGA_WITH_CAM_Y"] = dc["OMEGA_WITH_CAM_Y"]
            save_dc["OMEGA_WITH_CAM_Z"] = dc["OMEGA_WITH_CAM_Z"]

            save_dc["OMEGA_NO_CAM_X"] = dc["OMEGA_NO_CAM_X"]
            save_dc["OMEGA_NO_CAM_Y"] = dc["OMEGA_NO_CAM_Y"]
            save_dc["OMEGA_NO_CAM_Z"] = dc["OMEGA_NO_CAM_Z"]

            save_dc["ACC_WITH_CAM_X"] = dc["ACC_WITH_CAM_X"]
            save_dc["ACC_WITH_CAM_Y"] = dc["ACC_WITH_CAM_Y"]
            save_dc["ACC_WITH_CAM_Z"] = dc["ACC_WITH_CAM_Z"]

            save_dc["ACC_NO_CAM_X"] = dc["ACC_NO_CAM_X"]
            save_dc["ACC_NO_CAM_Y"] = dc["ACC_NO_CAM_Y"]
            save_dc["ACC_NO_CAM_Z"] = dc["ACC_NO_CAM_Z"]

            save_dc["ACC_REL_CAM_X"] = dc["ACC_REL_CAM_X"]
            save_dc["ACC_REL_CAM_Y"] = dc["ACC_REL_CAM_Y"]
            save_dc["ACC_REL_CAM_Z"] = dc["ACC_REL_CAM_Z"]

            save_dc["ANGLE_BY_PRE"] = dc["ANGLE_BY_PRE"]

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
