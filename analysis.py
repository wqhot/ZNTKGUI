# -*- coding: utf-8 -*-
from ui.Ui_analysis import Ui_Dialog
import csv
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation
import matplotlib
import math
from scipy.optimize import minimize
# matplotlib.use("Qt5Agg")  # 声明使用QT5


class Estimate():
    def __init__(self, analysisData={}, analysisZtData={}, data_stamp=np.array([])):
        self.analysisData = analysisData
        self.analysisZtData = analysisZtData
        self.data_stamp = data_stamp
        self.res = minimize(fun=self.func, x0=[0.0], method='Nelder-Mead',
                            options={'maxiter': 1000, 'disp': True,
                                     'return_all': True, 'eps': 0.001, 'initial_simplex': [[0.0], [-3 * (self.data_stamp[1] - self.data_stamp[0])]]})

    def func(self, x):
        errors = []
        delay = x[0]
        if delay >= 0:
            index = np.where(self.data_stamp <=
                             self.data_stamp[-1] - delay)[0]  # 取前部
            indexZt = range(len(self.data_stamp) - len(index),
                            len(self.data_stamp), 1)  # 取后部
        else:
            index = np.where(self.data_stamp >=
                             self.data_stamp[0] - delay)[0]  # 取后部
            indexZt = range(0, len(index), 1)  # 取前部
        for key, ztKey in zip(self.analysisData.keys(), self.analysisZtData.keys()):
            delayAnalysisData = self.analysisData[key][index]
            delayAnalysisZtData = self.analysisZtData[ztKey][indexZt]
            error = delayAnalysisData - delayAnalysisZtData
            e = np.std(error)
            errors.append(e)
        err = sum(errors) / len(errors)
        print([delay, err, errors])
        return err


class analysisData():
    def __init__(self, wnd, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.figHist = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvasHist = FigureCanvas(self.figHist)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes = self.fig.add_subplot(111)
        self.axesHist1 = self.figHist.add_subplot(121)
        self.axesHist1.set_title("cost of eul")
        self.axesHist2 = self.figHist.add_subplot(122)
        self.axesHist2.set_title("cost of cam")
        self.data = {}
        self.ztData = {}
        self.zxData = {}
        self.wnd = wnd
        self.analysisData = {}
        self.analysisZtData = {}
        self.analysisZxData = {}
        self.analysisDataZeros = {}
        self.analysisZtDataZeros = {}
        self.analysisZxDataZeros = {}
        self.fuData = []
        self.startStamp = 0
        # 标志值设为none
        self._ind = None
        self.moveFlag = False
        self.startX = -1.0
        self.endX = 1.0
        self.startY = -10.0
        self.endY = 10.0
        self.line1 = None
        self.line2 = None
        self.rq_points = []
        self.rq_lines = []
        self.fill_bars = []
        self.drawLine()
        self.canvas.mpl_connect('button_press_event', self.onclick)
        self.canvasHist.mpl_connect('button_press_event', self.drawTest)
        self.canvas.mpl_connect('button_release_event',
                                self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event',
                                self.motion_notify_callback)

    def drawTest(self, event, emin=None, emax=None, cmin=None, cmax=None):
        if event.button == 1 and event.dblclick == True:
            if 'cost_of_eul' in self.data.keys():
                plt.hist(x=self.data['cost_of_eul'], bins=4000, range=(0, 1.0))
                avg = np.average(self.data['cost_of_eul'])
                std = np.std(self.data['cost_of_eul'])
                s = 'avg: %.2fms \nstd: %.2f' % (avg, std)
                maxx = self.data['cost_of_eul'].max() if emax is None else emax
                plt.text(0.0, maxx - 0.2, s)
                plt.show()
            if 'cost_of_cam' in self.data.keys():
                plt.clear()
                plt.hist(x=self.data['cost_of_cam'], bins=4000)
                avg = np.average(self.data['cost_of_cam'])
                std = np.std(self.data['cost_of_cam'])
                s = 'avg: %.2fms \nstd: %.2f' % (avg, std)
                maxx = self.data['cost_of_cam'].max() if cmax is None else cmax
                plt.text(0.0, maxx - 0.15, s)
                plt.show()

    def drawHist(self, emin=None, emax=None, cmin=None, cmax=None):
        if 'cost_of_eul' in self.data.keys():
            self.axesHist1.clear()
            if emin is None or emax is None:
                self.axesHist1.hist(
                    x=self.data['cost_of_eul'], bins=4000, orientation='horizontal', histtype='step')
            else:
                if emin > emax:
                    emax = emin
                self.axesHist1.hist(x=self.data['cost_of_eul'], bins=4000, range=(
                    emin, emax), orientation='horizontal', histtype='step')
            avg = np.average(self.data['cost_of_eul'])
            std = np.std(self.data['cost_of_eul'])
            s = 'avg: %.2fms \nstd: %.2f' % (avg, std)
            maxx = self.data['cost_of_eul'].max() if emax is None else emax
            self.axesHist1.text(0.0, maxx - 0.2, s)
        if 'cost_of_cam' in self.data.keys():
            self.axesHist2.clear()
            if cmin is None or cmax is None:
                self.axesHist2.hist(
                    x=self.data['cost_of_cam'], bins=4000, orientation='horizontal', histtype='step')
            else:
                if cmin > cmax:
                    cmax = cmin
                self.axesHist2.hist(x=self.data['cost_of_cam'], bins=4000, range=(
                    cmin, cmax), orientation='horizontal', histtype='step')
            avg = np.average(self.data['cost_of_cam'])
            std = np.std(self.data['cost_of_cam'])
            s = 'avg: %.2fms \nstd: %.2f' % (avg, std)
            maxx = self.data['cost_of_cam'].max() if cmax is None else cmax
            self.axesHist2.text(0.0, maxx - 0.15, s)
        self.canvasHist.draw()
        self.canvasHist.flush_events()

    def drawLine(self):
        x1 = np.tile(self.startX, 100)
        x2 = np.tile(self.endX, 100)
        y1 = np.linspace(self.startY, self.endY, 100)
        self.line1, = self.axes.plot(x1, y1, marker='3', color='k')
        self.line2, = self.axes.plot(x2, y1, marker='4', color='k')

    # 返回pre cam的延时范围
    def getBoundary(self):
        if 'cost_of_eul' in self.data.keys() and 'cost_of_cam' in self.data.keys():
            return [self.data['cost_of_eul'].min(), self.data['cost_of_eul'].max(),
                    self.data['cost_of_cam'].min(), self.data['cost_of_cam'].max()]
        else:
            return [0, 0, 0, 0]

    def importData(self, fileName):
        title = []
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            title = next(reader)
        arr = np.loadtxt(fileName, delimiter=",", skiprows=1)
        col = 0
        for t in title:
            self.data[t] = arr[:, col]
            col = col + 1
        self.drawHist()
        return title

    def importZtData(self, fileName):
        title = []
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            title = next(reader)
        arr = np.loadtxt(fileName, delimiter=",", skiprows=1)
        col = 0
        for t in title:
            self.ztData[t] = arr[:, col]
            col = col + 1
        return title

    def importZxData(self, fileName):
        title = []
        with open(fileName, newline='') as f:
            reader = csv.reader(f)
            title = next(reader)
        arr = np.loadtxt(fileName, delimiter=",", skiprows=1)
        col = 0
        for t in title:
            self.zxData[t] = arr[:, col]
            col = col + 1
        return title

    def selectDataCols(self, cols, all_cols):
        self.analysisData = {}
        self.analysisDataZeros = {}
        for col in cols:
            self.analysisData[col] = self.data[col]
        for col in all_cols:
            self.analysisDataZeros[col] = 0

    def selectZtDataCols(self, cols, all_cols):
        self.analysisZtData = {}
        self.analysisZtDataZeros = {}
        for col in cols:
            self.analysisZtData[col] = self.ztData[col]
        for col in all_cols:
            self.analysisZtDataZeros[col] = 0

    def selectZxDataCols(self, cols, all_cols):
        self.analysisZxData = {}
        self.analysisZxDataZeros = {}
        for col in cols:
            self.analysisZxData[col] = self.zxData[col]
        for col in all_cols:
            self.analysisZxDataZeros[col] = 0

    def setFuData(self, labels):
        self.fuData = labels

    def use_RQ(self):
        directory = QFileDialog.getOpenFileName(self.wnd,
                                                "保存的位置", "../rg.txt",
                                                "Text Files (*.txt)")
        if len(directory[0]) == 0:
            return None
        Rg = np.loadtxt(directory[0])
        data1 = self.data
        data2 = self.ztData
        analysisdata1 = self.analysisData
        analysisdata2 = self.analysisZtData
        analysisdatazero1 = self.analysisDataZeros
        analysisdatazero2 = self.analysisZtDataZeros
        indexStart_data = np.where(
            data1['stamp'] >= self.startX + self.startStamp)[0]
        indexStart_ztData = np.where(
            data2['stamp'] >= self.startX + self.startStamp)[0]

        indexEnd_data = np.where(
            data1['stamp'] <= self.endX + self.startStamp)[0]
        indexEnd_ztData = np.where(
            data2['stamp'] <= self.endX + self.startStamp)[0]
        index_data = np.intersect1d(indexStart_data, indexEnd_data)
        index_ztData = np.intersect1d(indexStart_ztData, indexEnd_ztData)
        data_stamp = data1['stamp'][index_data]
        ztData_stamp = data2['stamp'][index_ztData]
        analysisData = {}
        analysisZtData = {}
        # 时间戳减去初始值
        data_stamp = data_stamp - \
            np.tile(self.startStamp, data_stamp.shape)
        ztData_stamp = ztData_stamp - \
            np.tile(self.startStamp, ztData_stamp.shape)

        temp_x = data2['x_ang_cl'][index_ztData] - \
            np.tile(analysisdatazero2['x_ang_cl'],
                    data2['x_ang_cl'][index_ztData].shape)
        temp_y = np.zeros(shape=data2['x_ang_cl'][index_ztData].shape)
        temp_z = data2['z_ang_cl'][index_ztData] - \
            np.tile(analysisdatazero2['z_ang_cl'],
                    data2['z_ang_cl'][index_ztData].shape)
        temp_x_interp = np.interp(data_stamp,
                                  ztData_stamp,
                                  temp_x)
        temp_y_interp = np.interp(data_stamp,
                                  ztData_stamp,
                                  temp_y)
        temp_z_interp = -np.interp(data_stamp,
                                   ztData_stamp,
                                   temp_z)
        temp_interp = np.vstack(
            (temp_x_interp, temp_y_interp, temp_z_interp)).T
        R_zt = Rotation.from_euler('ZYX', temp_interp, degrees=True)
        temp_data = np.vstack((
            data1['quat_pre_x'],
            data1['quat_pre_y'],
            data1['quat_pre_z'],
            data1['quat_pre_w'])).T
        R_m = Rotation.from_quat(temp_data)

        if Rg.shape == (3, 4):
            r_m_new = np.zeros(R_m.as_matrix().shape)
            for i in range(len(R_m)):
                r_m = R_m[i].as_matrix()
                r_m_new[i, :, :] = Rg[:,:3] * r_m
            R_m_new = Rotation.from_matrix(r_m_new)
            R_m_euler_ = R_m_new.as_euler('ZYX', degrees=True)
        elif Rg.shape == (4, 4):
            q_m_new = np.zeros(temp_data.shape)
            for i in range(len(R_m)):
                q_m = R_m[i].as_quat()
                q_m_new[i, :] = np.array((Rg * np.matrix(q_m).T).T[0])
            R_m_new = Rotation.from_quat(q_m_new)
            R_m_euler_ = R_m_new.as_euler('ZYX', degrees=True)
            
        self.data['eul_x_R'] = R_m_euler_[:, 0]
        self.data['eul_y_R'] = R_m_euler_[:, 1]
        self.data['eul_z_R'] = R_m_euler_[:, 2]
        
        self.wnd.updateData(list(self.data.keys()))
        return None
        

    def cal_RQ(self):
        data1 = self.data
        data2 = self.ztData
        analysisdata1 = self.analysisData
        analysisdata2 = self.analysisZtData
        analysisdatazero1 = self.analysisDataZeros
        analysisdatazero2 = self.analysisZtDataZeros
        indexStart_data = np.where(
            data1['stamp'] >= self.startX + self.startStamp)[0]
        indexStart_ztData = np.where(
            data2['stamp'] >= self.startX + self.startStamp)[0]

        indexEnd_data = np.where(
            data1['stamp'] <= self.endX + self.startStamp)[0]
        indexEnd_ztData = np.where(
            data2['stamp'] <= self.endX + self.startStamp)[0]
        index_data = np.intersect1d(indexStart_data, indexEnd_data)
        index_ztData = np.intersect1d(indexStart_ztData, indexEnd_ztData)
        data_stamp = data1['stamp'][index_data]
        ztData_stamp = data2['stamp'][index_ztData]
        analysisData = {}
        analysisZtData = {}
        # 时间戳减去初始值
        data_stamp = data_stamp - \
            np.tile(self.startStamp, data_stamp.shape)
        ztData_stamp = ztData_stamp - \
            np.tile(self.startStamp, ztData_stamp.shape)

        temp_x = data2['x_ang_cl'][index_ztData] - \
            np.tile(analysisdatazero2['x_ang_cl'],
                    data2['x_ang_cl'][index_ztData].shape)
        temp_y = np.zeros(shape=data2['x_ang_cl'][index_ztData].shape)
        temp_z = data2['z_ang_cl'][index_ztData] - \
            np.tile(analysisdatazero2['z_ang_cl'],
                    data2['z_ang_cl'][index_ztData].shape)
        temp_x_interp = np.interp(data_stamp,
                                  ztData_stamp,
                                  temp_x)
        temp_y_interp = np.interp(data_stamp,
                                  ztData_stamp,
                                  temp_y)
        temp_z_interp = -np.interp(data_stamp,
                                   ztData_stamp,
                                   temp_z)
        temp_interp = np.vstack(
            (temp_x_interp, temp_y_interp, temp_z_interp)).T
        R_zt = Rotation.from_euler('ZYX', temp_interp, degrees=True)
        temp_data = np.vstack((
            data1['quat_pre_x'][index_data],
            data1['quat_pre_y'][index_data],
            data1['quat_pre_z'][index_data],
            data1['quat_pre_w'][index_data])).T
        R_m = Rotation.from_quat(temp_data)
        for bar in self.fill_bars:
            bar.remove()
        self.fill_bars = []
        if len(self.rq_points) > 4:
            # 选取范围内数据
            a = np.matrix(np.zeros((4, len(self.rq_points)))) # 测量值
            u = np.matrix(np.zeros((4, len(self.rq_points)))) # 转台值
            ga = np.matrix(np.zeros((4, len(self.rq_points)))) # 测量值
            gu = np.matrix(np.zeros((3, len(self.rq_points)))) # 转台值
            for i, p in enumerate(self.rq_points):
                stamp_index = np.argmin(np.abs(data_stamp - p))
                stamp_index_start = stamp_index
                stamp_index_end = stamp_index
                # 向左寻找
                while stamp_index_start > 0 and \
                      abs(temp_interp[stamp_index][0] - temp_interp[stamp_index_start][0]) <= 0.05 and \
                      abs(temp_interp[stamp_index][1] - temp_interp[stamp_index_start][1]) <= 0.05 and \
                      abs(temp_interp[stamp_index][2] - temp_interp[stamp_index_start][2]) <= 0.05:

                    stamp_index_start = stamp_index_start - 1
                # 向右寻找
                while stamp_index_end < len(data_stamp) and \
                      abs(temp_interp[stamp_index][0] - temp_interp[stamp_index_end][0]) <= 0.05 and \
                      abs(temp_interp[stamp_index][1] - temp_interp[stamp_index_end][1]) <= 0.05 and \
                      abs(temp_interp[stamp_index][2] - temp_interp[stamp_index_end][2]) <= 0.05:

                    stamp_index_end = stamp_index_end + 1
                y1 = len(data_stamp[stamp_index_start:stamp_index_end+1])*[self.endY]
                y0 = len(data_stamp[stamp_index_start:stamp_index_end+1])*[self.startY]
                x = data_stamp[stamp_index_start:stamp_index_end+1]
                bar = self.axes.fill_between(x, y1, y0, facecolor='gray')
                self.fill_bars.append(bar)
                if 'acc_with_cam_x' in data1.keys() and \
                   'acc_with_cam_y' in data1.keys() and \
                   'acc_with_cam_z' in data1.keys():
                        R_zt_mean = R_zt[stamp_index_start:stamp_index_end+1].mean()
                        g_zt0 = np.matrix([[0],[0],[-9.8015]])
                        g_zt = R_zt_mean.as_matrix() * g_zt0
                        g_m_x = np.average(data1['acc_with_cam_x'][stamp_index_start:stamp_index_end+1])
                        g_m_y = np.average(data1['acc_with_cam_y'][stamp_index_start:stamp_index_end+1])
                        g_m_z = np.average(data1['acc_with_cam_z'][stamp_index_start:stamp_index_end+1])
                        g_m = np.matrix([g_m_x, g_m_y, g_m_z, 1.0])
                        ga[:, i] = g_m.T
                        gu[:, i] = g_zt
                a[:, i] = np.matrix(R_m[stamp_index_start:stamp_index_end+1].mean().as_quat()).T
                u[:, i] = np.matrix(R_zt[stamp_index_start:stamp_index_end+1].mean().as_quat()).T
            self.canvas.draw()
            self.canvas.flush_events()
        else:
            a = np.matrix(R_m.as_quat().T)
            u = np.matrix(R_zt.as_quat().T)
        RQ = u * a.T * (a * a.T).I
        if np.linalg.norm(np.linalg.norm(ga)) != 0 and np.linalg.norm(np.linalg.norm(gu)) != 0:
            Rg = gu * ga.T * (ga * ga.T).I
            print("======Rg======")
            print(Rg)
            print("======Rg======")
            directory = QFileDialog.getSaveFileName(self.wnd,
                                                    "保存的位置", "../rg.txt",
                                                    "Text Files (*.txt)")
            if len(directory[0]) != 0:
                np.savetxt(directory[0], Rg)
            r_m_new = np.zeros(R_m.as_matrix().shape)
            for i in range(len(R_m)):
                r_m = R_m[i].as_matrix()
                r_m_new[i, :, :] = Rg[:,:3] * r_m
            R_m_new = Rotation.from_matrix(r_m_new)
            R_m_euler_ = R_m_new.as_euler('ZYX', degrees=True)
        else:
            print("======RQ======")
            print(RQ)
            print("======RQ======")
            directory = QFileDialog.getSaveFileName(self.wnd,
                                                    "保存的位置", "../rq.txt",
                                                    "Text Files (*.txt)")
            if len(directory[0]) != 0:
                np.savetxt(directory[0], RQ)
            q_m_new = np.zeros(temp_data.shape)
            for i in range(len(R_m)):
                q_m = R_m[i].as_quat()
                q_m_new[i, :] = np.array((RQ * np.matrix(q_m).T).T[0])
            R_m_new = Rotation.from_quat(q_m_new)
            R_m_euler_ = R_m_new.as_euler('ZYX', degrees=True)
        analysisData['ex'] = R_m_euler_[:, 0]
        analysisData['ey'] = R_m_euler_[:, 1]
        analysisData['ez'] = R_m_euler_[:, 2]
        analysisZtData['ex'] = temp_interp[:, 0]
        analysisZtData['ey'] = temp_interp[:, 1]
        analysisZtData['ez'] = temp_interp[:, 2]
        estimate = Estimate(analysisData, analysisZtData, data_stamp)
        res = estimate.res
        directory = QFileDialog.getSaveFileName(self.wnd,
                                                "保存的位置", "./history/rq.csv",
                                                "CSV Files (*.csv)")
        if len(directory[0]) != 0:
            analysisData['stamp'] = data_stamp + self.startStamp
            df = pd.DataFrame.from_dict(analysisData)
            df.to_csv(directory[0], index=False)
        
        return res

    def estimateDelay(self):
        data1 = []
        data2 = []
        analysisdata1 = []
        analysisdata2 = []
        analysisdatazero1 = []
        analysisdatazero2 = []
        analysis_quat_meas = []
        analysis_quat_zt = []
        analysis_quat_bt = []
        cal_imu_zt_R = False
        cal_estimate = True
        if len(self.analysisData.keys()) == 0 and len(self.analysisZtData.keys()) == 0 and len(self.analysisZxData.keys()) == 0:
            data1 = self.data
            data2 = self.ztData
            analysisdatazero1 = self.analysisDataZeros
            analysisdatazero2 = self.analysisZtDataZeros
            cal_imu_zt_R = True
            cal_estimate = False
        elif len(self.analysisData.keys()) == 0 and len(self.analysisZtData.keys()) == len(self.analysisZxData.keys()):
            data1 = self.zxData
            data2 = self.ztData
            analysisdata1 = self.analysisZxData
            analysisdata2 = self.analysisZtData
            analysisdatazero1 = self.analysisZxDataZeros
            analysisdatazero2 = self.analysisZtDataZeros
        elif len(self.analysisZtData.keys()) == 0 and len(self.analysisData.keys()) == len(self.analysisZxData.keys()):
            data1 = self.zxData
            data2 = self.data
            analysisdata1 = self.analysisZxData
            analysisdata2 = self.analysisData
            analysisdatazero1 = self.analysisZxDataZeros
            analysisdatazero2 = self.analysisDataZeros
        elif len(self.analysisZxData.keys()) == 0 and len(self.analysisData.keys()) == len(self.analysisZtData.keys()):
            data1 = self.data
            data2 = self.ztData
            analysisdata1 = self.analysisData
            analysisdata2 = self.analysisZtData
            analysisdatazero1 = self.analysisDataZeros
            analysisdatazero2 = self.analysisZtDataZeros
            cal_imu_zt_R = True
        else:
            return None
        indexStart_data = np.where(
            data1['stamp'] >= self.startX + self.startStamp)[0]
        indexStart_ztData = np.where(
            data2['stamp'] >= self.startX + self.startStamp)[0]

        indexEnd_data = np.where(
            data1['stamp'] <= self.endX + self.startStamp)[0]
        indexEnd_ztData = np.where(
            data2['stamp'] <= self.endX + self.startStamp)[0]
        index_data = np.intersect1d(indexStart_data, indexEnd_data)
        index_ztData = np.intersect1d(indexStart_ztData, indexEnd_ztData)
        data_stamp = data1['stamp'][index_data]
        ztData_stamp = data2['stamp'][index_ztData]
        analysisData = {}
        analysisZtData = {}
        # 时间戳减去初始值
        data_stamp = data_stamp - \
            np.tile(self.startStamp, data_stamp.shape)
        ztData_stamp = ztData_stamp - \
            np.tile(self.startStamp, ztData_stamp.shape)
        if cal_estimate:
            for key in analysisdata1.keys():
                analysisData[key] = analysisdata1[key][index_data] - \
                    np.tile(analysisdatazero1[key],
                            analysisdata1[key][index_data].shape)
                if key in self.fuData:
                    analysisData[key] = -analysisData[key]
            # 对于zt数据需要插值
            for key in analysisdata2.keys():
                temp = analysisdata2[key][index_ztData] - \
                    np.tile(
                        analysisdatazero2[key], analysisdata2[key][index_ztData].shape)
                analysisZtData[key] = np.interp(data_stamp,
                                                ztData_stamp,
                                                temp)
                if key in self.fuData:
                    analysisZtData[key] = -analysisZtData[key]
        # if cal_imu_zt_R:
        #     temp_x = data2['x_ang_cl'][index_ztData] - \
        #         np.tile(analysisdatazero2['x_ang_cl'],
        #                 data2['x_ang_cl'][index_ztData].shape)
        #     temp_y = np.zeros(shape=data2['x_ang_cl'][index_ztData].shape)
        #     temp_z = data2['z_ang_cl'][index_ztData] - \
        #         np.tile(analysisdatazero2['z_ang_cl'],
        #                 data2['z_ang_cl'][index_ztData].shape)
        #     temp_x_interp = np.interp(data_stamp,
        #                               ztData_stamp,
        #                               temp_x)
        #     temp_y_interp = np.interp(data_stamp,
        #                               ztData_stamp,
        #                               temp_y)
        #     temp_z_interp = -np.interp(data_stamp,
        #                                ztData_stamp,
        #                                temp_z)
        #     temp_interp = np.vstack(
        #         (temp_x_interp, temp_y_interp, temp_z_interp)).T
        #     R_zt = Rotation.from_euler('ZYX', temp_interp, degrees=True)
        #     temp_data = np.vstack((
        #         data1['quat_pre_x'][index_data],
        #         data1['quat_pre_y'][index_data],
        #         data1['quat_pre_z'][index_data],
        #         data1['quat_pre_w'][index_data])).T
        #     R_m = Rotation.from_quat(temp_data)
        #     a = np.matrix(R_m.as_quat().T)
        #     u = np.matrix(R_zt.as_quat().T)
        #     RQ = u * a.T * (a * a.T).I
        #     print("======RQ======")
        #     print(RQ)
        #     print("======RQ======")
        #     q_m_new = np.zeros(temp_data.shape)
        #     for i in range(len(R_m)):
        #         q_m = R_m[i].as_quat()
        #         q_m_new[i, :] = np.array((RQ * np.matrix(q_m).T).T[0])
        #     R_m_new = Rotation.from_quat(q_m_new)
        #     print("a")

        res = None
        if cal_estimate:
            estimate = Estimate(analysisData, analysisZtData, data_stamp)
            res = estimate.res
        print(data_stamp[0])
        return res

    def analysis(self):
        # 对齐时间戳，取交集
        startStamp_data = 0
        startStamp_ztData = 0
        if 'stamp' in self.data.keys():
            startStamp_data = self.data['stamp'][0]
        if 'stamp' in self.ztData.keys():
            startStamp_ztData = self.ztData['stamp'][0]
        useZx = False
        if 'stamp' in self.zxData.keys():
            useZx = True
        self.startStamp = startStamp_data if startStamp_data > startStamp_ztData else startStamp_ztData
        if useZx:
            startStamp_zxData = self.zxData['stamp'][0]
            self.startStamp = self.startStamp if self.startStamp > startStamp_zxData else startStamp_zxData

        indexStart_data = []
        indexStart_ztData = []
        if 'stamp' in self.data.keys():
            indexStart_data = np.where(
                self.data['stamp'] >= self.startStamp)[0]
        if 'stamp' in self.ztData.keys():
            indexStart_ztData = np.where(
                self.ztData['stamp'] >= self.startStamp)[0]
        indexStart_zxData = []
        if useZx:
            indexStart_zxData = np.where(
                self.zxData['stamp'] >= self.startStamp)[0]
        endStamp_data = math.inf
        endStamp_ztData = math.inf
        if 'stamp' in self.data.keys():
            endStamp_data = self.data['stamp'][-1]
        if 'stamp' in self.ztData.keys():
            endStamp_ztData = self.ztData['stamp'][-1]
        endStamp = endStamp_data if endStamp_data < endStamp_ztData else endStamp_ztData
        endStamp_zxData = []
        if useZx:
            endStamp_zxData = self.zxData['stamp'][-1]
            endStamp = endStamp if endStamp < endStamp_zxData else endStamp_zxData
        indexEnd_data = []
        indexEnd_ztData = []
        if 'stamp' in self.data.keys():
            indexEnd_data = np.where(self.data['stamp'] <= endStamp)[0]
        if 'stamp' in self.ztData.keys():
            indexEnd_ztData = np.where(self.ztData['stamp'] <= endStamp)[0]
        indexEnd_zxData = []
        if useZx:
            indexEnd_zxData = np.where(self.zxData['stamp'] <= endStamp)[0]

        index_data = np.intersect1d(indexStart_data, indexEnd_data)
        index_ztData = np.intersect1d(indexStart_ztData, indexEnd_ztData)
        zxData_stamp = []
        index_zxData = []
        if useZx:
            index_zxData = np.intersect1d(indexStart_zxData, indexEnd_zxData)
            zxData_stamp = self.zxData['stamp'][index_zxData]
        data_stamp = 0
        ztData_stamp = 0
        if 'stamp' in self.data.keys():
            data_stamp = self.data['stamp'][index_data]
        if 'stamp' in self.ztData.keys():
            ztData_stamp = self.ztData['stamp'][index_ztData]
        analysisData = {}
        analysisZtData = {}
        analysisZxData = {}
        # 时间戳减去初始值
        data_stamp = data_stamp - \
            np.tile(self.startStamp, (len(index_data),))
        ztData_stamp = ztData_stamp - \
            np.tile(self.startStamp, (len(index_ztData),))
        if useZx:
            zxData_stamp = zxData_stamp - \
                np.tile(self.startStamp, (len(index_zxData),))
        self.startX = 0.0
        self.endX = endStamp - self.startStamp
        for key in self.analysisData.keys():
            analysisData[key] = self.analysisData[key][index_data] - \
                np.tile(
                    self.analysisDataZeros[key], self.analysisData[key][index_data].shape)
        # 对于zt数据需要插值
        for key in self.analysisZtData.keys():
            temp = self.analysisZtData[key][index_ztData] - \
                np.tile(
                    self.analysisZtDataZeros[key], self.analysisZtData[key][index_ztData].shape)
            analysisZtData[key] = np.interp(data_stamp,
                                            ztData_stamp,
                                            temp)
        # 对于zx数据需要插值
        if useZx:
            for key in self.analysisZxData.keys():
                temp = self.analysisZxData[key][index_zxData] - \
                    np.tile(
                        self.analysisZxDataZeros[key], self.analysisZxData[key][index_zxData].shape)
                analysisZxData[key] = np.interp(data_stamp,
                                                zxData_stamp,
                                                temp)
        # 开始绘图
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.startY = 360.0
        self.endY = -360.0
        for key in analysisData.keys():
            if key in self.fuData:
                self.axes.plot(data_stamp,
                               -analysisData[key], label=key)
                maxy = (-analysisData[key]).max()
                miny = (-analysisData[key]).min()
            else:
                self.axes.plot(data_stamp,
                               analysisData[key], label=key)
                maxy = (analysisData[key]).max()
                miny = (analysisData[key]).min()
            self.startY = self.startY if self.startY < miny else miny
            self.endY = self.endY if self.endY > maxy else maxy
        for key in analysisZtData.keys():
            if key in self.fuData:
                self.axes.plot(data_stamp,
                               -analysisZtData[key], label=key)
                maxy = (-analysisZtData[key]).max()
                miny = (-analysisZtData[key]).min()
            else:
                self.axes.plot(data_stamp,
                               analysisZtData[key], label=key)
                maxy = (analysisZtData[key]).max()
                miny = (analysisZtData[key]).min()
            self.startY = self.startY if self.startY < miny else miny
            self.endY = self.endY if self.endY > maxy else maxy
        for key in analysisZxData.keys():
            if key in self.fuData:
                self.axes.plot(data_stamp,
                               -analysisZxData[key], label=key)
                maxy = (-analysisZxData[key]).max()
                miny = (-analysisZxData[key]).min()
            else:
                self.axes.plot(data_stamp,
                               analysisZxData[key], label=key)
                maxy = (analysisZxData[key]).max()
                miny = (analysisZxData[key]).min()
            self.startY = self.startY if self.startY < miny else miny
            self.endY = self.endY if self.endY > maxy else maxy
        self.axes.legend()
        self.drawLine()
        self.canvas.draw()
        self.canvas.flush_events()
        # self.axes.show()
        # plt.show()

    def drawRQ_Line(self):
        for line_temp in self.rq_lines:
            line_temp.remove()
        self.rq_lines = []
        y1 = np.linspace(self.startY, self.endY, 100)
        for i, p in enumerate(self.rq_points):
            x1 = np.tile(p, 100)
            line_temp, = self.axes.plot(x1, y1, marker='+', color='b')
            self.rq_lines.append(line_temp)
        self.canvas.draw()
        self.canvas.flush_events()

    def onclick(self, event):

        if event.button == 1 and event.dblclick == False:
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            if abs(x - self.startX) < 0.5:
                self._ind = 0
                self.moveFlag = True
            elif abs(x - self.endX) < 0.5:
                self._ind = 1
                self.moveFlag = True
            else:
                self._ind = None
                self.moveFlag = False

        if event.button == 1 and event.dblclick == True:
            x = event.xdata
            stamp = x + self.startStamp
            delta1 = np.abs(self.data['stamp'] -
                            np.tile(stamp, self.data['stamp'].shape))
            delta2 = np.abs(
                self.ztData['stamp'] - np.tile(stamp, self.ztData['stamp'].shape))
            index1 = np.argmin(delta1)
            index2 = np.argmin(delta2)
            for key in self.data.keys():
                self.analysisDataZeros[key] = self.data[key][index1]
            for key in self.ztData.keys():
                self.analysisZtDataZeros[key] = self.ztData[key][index2]
            if 'stamp' in self.zxData.keys():
                delta3 = np.abs(
                    self.zxData['stamp'] - np.tile(stamp, self.zxData['stamp'].shape))
                index3 = np.argmin(delta3)
                for key in self.zxData.keys():
                    self.analysisZxDataZeros[key] = self.zxData[key][index3]
            self.analysis()
            # print(self.analysisDataZeros)
            # print(self.analysisZtDataZeros)
        if event.button == 2:
            x = event.xdata
            stamp = x
            if self.endX < stamp or self.startX > stamp:
                return
            # 寻找self.rq_points中与之类似的点
            for p in self.rq_points:
                if abs(p - stamp) < 5.0:
                    self.rq_points.remove(p)
                    self.drawRQ_Line()
                    return
            self.rq_points.append(stamp)
            self.drawRQ_Line()

    def button_release_callback(self, event):
        if event.button == 1:
            self.moveFlag = True
            self._ind = None

    def motion_notify_callback(self, event):
        x, y = event.xdata, event.ydata
        if not self.moveFlag:
            return
        if x is None or y is None:
            return
        if self._ind is None:
            return
        if self._ind == 0:
            self.startX = x
        elif self._ind == 1:
            self.endX = x
        self.line1.remove()
        self.line2.remove()
        self.drawLine()
        self.canvas.draw()
        self.canvas.flush_events()


class analysisDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(analysisDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("分析")
        self.setMinimumSize(0, 0)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.datalabels = []
        self.ztdatalabels = []
        self.zxdatalabels = []
        self.selectDatalabels = []
        self.selectZtDatalabels = []
        self.selectZxDatalabels = []
        self.fuDatalabels = []
        # 第五步：定义MyFigure类的一个实例
        self.F = analysisData(self, width=3, height=2, dpi=100)
        # self.F.importData('./history/2020_06_18_13_44_04(fy1).csv')
        # self.F.importZtData('./history/2020-06-16-15_51_55_zt(fy).csv')
        # datacols1 = ['eul_x', 'cam_x', 'imu_x']
        # datacols2 = ['secondAxisPos']
        # self.F.selectDataCols(datacols1)
        # self.F.selectZtDataCols(datacols2)
        # self.F.analysis()
        #
        self.toolbar = NavigationToolbar(self.F.canvas, self)
        self.figureLayout.addWidget(self.toolbar)
        self.figureLayout.addWidget(self.F.canvas)
        self.histLayout.addWidget(self.F.canvasHist)
        self.pushButton_opendata.clicked.connect(self.openData)
        self.pushButton_openztdata.clicked.connect(self.openZtData)
        self.pushButton_openztdata_2.clicked.connect(self.openZxData)
        self.listWidget_1.doubleClicked.connect(self.addData)
        self.listWidget_2.doubleClicked.connect(self.delData)
        self.pushButton_2.clicked.connect(self.addData)
        self.pushButton.clicked.connect(self.delData)
        self.pushButton_3.clicked.connect(self.addFuData)
        self.pushButton_4.clicked.connect(self.estimateDelay)
        self.pushButton_5.clicked.connect(self.cal_RQ)
        self.pushButton_6.clicked.connect(self.use_RQ)
        self.horizontalSlider.valueChanged.connect(self.eulBaundaryChange)
        self.horizontalSlider_2.valueChanged.connect(self.camBaundaryChange)
        # 补充：另创建一个实例绘图并显示
        # self.plotother()

    def eulBaundaryChange(self):
        self.lineEdit_3.setText(str(self.horizontalSlider.value()))
        [emin, emax, cmin, cmax] = self.F.getBoundary()
        emax = self.horizontalSlider.value()
        cmax = self.horizontalSlider_2.value()
        self.F.drawHist(emin=emin, emax=emax, cmin=cmin, cmax=cmax)

    def camBaundaryChange(self):
        self.lineEdit_4.setText(str(self.horizontalSlider_2.value()))
        [emin, emax, cmin, cmax] = self.F.getBoundary()
        emax = self.horizontalSlider.value()
        cmax = self.horizontalSlider_2.value()
        self.F.drawHist(emin=emin, emax=emax, cmin=cmin, cmax=cmax)

    def refresh(self):
        self.F.selectDataCols(self.selectDatalabels, self.datalabels)
        self.F.selectZtDataCols(self.selectZtDatalabels, self.ztdatalabels)
        self.F.selectZxDataCols(self.selectZxDatalabels, self.zxdatalabels)
        self.F.setFuData(self.fuDatalabels)
        self.F.analysis()
        # self.figureLayout.removeWidget(self.toolbar)
        # self.figureLayout.removeWidget(self.F.canvas)
        # self.figureLayout.addWidget(self.toolbar)
        # self.figureLayout.addWidget(self.F.canvas)

    def use_RQ(self):
        res = self.F.use_RQ()
        if res is None:
            return
        print(res)
        std = res.fun
        delay = res.x[0]
        self.doubleSpinBox_2.setValue(std)
        self.doubleSpinBox.setValue(delay)

    def cal_RQ(self):
        res = self.F.cal_RQ()
        if res is None:
            return
        print(res)
        std = res.fun
        delay = res.x[0]
        self.doubleSpinBox_2.setValue(std)
        self.doubleSpinBox.setValue(delay)

    def estimateDelay(self):
        res = self.F.estimateDelay()
        if res is None:
            return
        print(res)
        std = res.fun
        delay = res.x[0]
        self.doubleSpinBox_2.setValue(std)
        self.doubleSpinBox.setValue(delay)

    def addFuData(self):
        row = self.listWidget_1.currentRow()
        if row < 0:
            return
        label = self.listWidget_1.currentItem().text()
        item = self.listWidget_1.takeItem(row)
        self.fuDatalabels.append(label)
        if label in self.datalabels:
            self.selectDatalabels.append(label)
        elif label in self.ztdatalabels:
            self.selectZtDatalabels.append(label)
        else:
            self.selectZxDatalabels.append(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
        labels.extend(self.selectZxDatalabels)
        self.listWidget_2.clear()
        for item in labels:
            self.listWidget_2.addItem(item)
        self.refresh()

    def addData(self):
        row = self.listWidget_1.currentRow()
        if row < 0:
            return
        label = self.listWidget_1.currentItem().text()
        item = self.listWidget_1.takeItem(row)
        if label in self.datalabels:
            self.selectDatalabels.append(label)
        elif label in self.ztdatalabels:
            self.selectZtDatalabels.append(label)
        else:
            self.selectZxDatalabels.append(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
        labels.extend(self.selectZxDatalabels)
        self.listWidget_2.clear()
        for item in labels:
            self.listWidget_2.addItem(item)
        self.refresh()

    def delData(self):
        row = self.listWidget_2.currentRow()
        if row < 0:
            return
        label = self.listWidget_2.currentItem().text()
        item = self.listWidget_2.takeItem(row)
        if label in self.fuDatalabels:
            self.fuDatalabels.remove(label)
        if label in self.datalabels:
            self.selectDatalabels.remove(label)
        elif label in self.ztdatalabels:
            self.selectZtDatalabels.remove(label)
        else:
            self.selectZxDatalabels.remove(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
        labels.extend(self.selectZxDatalabels)
        self.listWidget_2.clear()
        for item in labels:
            self.listWidget_2.addItem(item)
        self.listWidget_1.addItem(label)
        self.refresh()

    def updateData(self, title):
        self.datalabels = title
        self.datalabels.remove('stamp')
        labels = []
        labels.extend(self.datalabels)
        labels.extend(self.ztdatalabels)
        labels.extend(self.zxdatalabels)
        self.listWidget_1.clear()
        for item in labels:
            if item not in ['cost_of_eul', 'cost_of_cam', 'cost_of_update']:
                self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        [emin, emax, cmin, cmax] = self.F.getBoundary()
        self.horizontalSlider.setMinimum(math.floor(emin))
        self.horizontalSlider.setMaximum(math.ceil(emax))
        self.horizontalSlider.setValue(math.ceil(emax))
        self.lineEdit_3.setText(str(math.ceil(emax)))
        self.horizontalSlider_2.setMinimum(math.floor(cmin))
        self.horizontalSlider_2.setMaximum(math.ceil(cmax))
        self.horizontalSlider_2.setValue(math.ceil(cmax))
        self.lineEdit_4.setText(str(math.ceil(cmax)))
        self.refresh()

    def openData(self):
        directory = QFileDialog.getOpenFileName(self,
                                                "getOpenFileName", "./history/",
                                                "Csv Files (*.csv)")
        if len(directory[0]) == 0:
            return
        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.lineEdit.setText(directory[0])
        self.datalabels = self.F.importData(directory[0])
        self.datalabels.remove('stamp')
        labels = []
        labels.extend(self.datalabels)
        labels.extend(self.ztdatalabels)
        labels.extend(self.zxdatalabels)
        self.listWidget_1.clear()
        for item in labels:
            if item not in ['cost_of_eul', 'cost_of_cam', 'cost_of_update']:
                self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        [emin, emax, cmin, cmax] = self.F.getBoundary()
        self.horizontalSlider.setMinimum(math.floor(emin))
        self.horizontalSlider.setMaximum(math.ceil(emax))
        self.horizontalSlider.setValue(math.ceil(emax))
        self.lineEdit_3.setText(str(math.ceil(emax)))
        self.horizontalSlider_2.setMinimum(math.floor(cmin))
        self.horizontalSlider_2.setMaximum(math.ceil(cmax))
        self.horizontalSlider_2.setValue(math.ceil(cmax))
        self.lineEdit_4.setText(str(math.ceil(cmax)))
        self.refresh()

    def openZtData(self):
        directory = QFileDialog.getOpenFileName(self,
                                                "getOpenFileName", "./history/",
                                                "Csv Files (*.csv)")
        if len(directory[0]) == 0:
            return
        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.lineEdit_2.setText(directory[0])
        self.ztdatalabels = self.F.importZtData(directory[0])
        self.ztdatalabels.remove('stamp')
        labels = []
        labels.extend(self.datalabels)
        labels.extend(self.ztdatalabels)
        labels.extend(self.zxdatalabels)
        self.listWidget_1.clear()
        for item in labels:
            if item not in ['cost_of_eul', 'cost_of_cam', 'cost_of_update']:
                self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.refresh()

    def openZxData(self):
        directory = QFileDialog.getOpenFileName(self,
                                                "getOpenFileName", "./history/",
                                                "Csv Files (*.csv)")
        if len(directory[0]) == 0:
            return
        self.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.lineEdit_5.setText(directory[0])
        self.zxdatalabels = self.F.importZxData(directory[0])
        self.zxdatalabels.remove('stamp')
        labels = []
        labels.extend(self.datalabels)
        labels.extend(self.ztdatalabels)
        labels.extend(self.zxdatalabels)
        self.listWidget_1.clear()
        for item in labels:
            if item not in ['cost_of_eul', 'cost_of_cam', 'cost_of_update']:
                self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.refresh()


# test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = analysisDialog()
    main.show()
    # app.installEventFilter(main)
    sys.exit(app.exec_())
