# -*- coding: utf-8 -*-
import sys
import socket

from Ui_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QFileDialog, QTabWidget, QMainWindow, QMessageBox, QTableWidgetItem

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QProcess

from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont

from PyQt5.QtWidgets import QLabel, QWidget

import numpy as np
import pyqtgraph as pg
from recvData import RecvData
import threading
import time
import math
import os
import pyqtgraph.opengl as gl
import cv2

# __POSE_BY_CAM = 4
# __ANGLE_BY_CAM = 16
# __DT_BY_CAM = 32
# __POSE_BY_UPDATE = 40
# __ANGLE_BY_UPDATE = 52
# __DT_BY_UPDATE = 68
# __POSE_BY_PRE = 76
# __ANGLE_BY_PRE = 88
# __DT_BY_PRE = 104
# __DT_OF_FRAME = 112
# __THRESOLD = 120
# __COST_OF_IMG = 124
# __LENGTH = 133
DICT_NAME_LIST = ["POSE_BY_CAM", "ANGLE_BY_CAM", "DT_BY_CAM",
                  "POSE_BY_UPDATE", "ANGLE_BY_UPDATE", "DT_BY_UPDATE",
                  "POSE_BY_PRE", "ANGLE_BY_PRE", "DT_BY_PRE",
                  "DT_OF_FRAME", "THRESOLD", "COST_OF_IMG",
                  "EUL_BY_CAM_X", "EUL_BY_UPDATE_X", "EUL_BY_PRE_X",
                  "EUL_BY_CAM_Y", "EUL_BY_UPDATE_Y", "EUL_BY_PRE_Y",
                  "EUL_BY_CAM_Z", "EUL_BY_UPDATE_Z", "EUL_BY_PRE_Z"]
DICT_TYPE_LIST = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0]

class mywindow(QMainWindow, Ui_MainWindow):  # 这个窗口继承了用QtDesignner 绘制的窗口

    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.lsts = {}
        index = 0

        for key in DICT_NAME_LIST:
            self.lsts[key] = [DICT_TYPE_LIST[index]] * 3600
            index = index + 1
        a_2 = pg.AxisItem("left")
        a_3 = pg.AxisItem("right")

        self.pw = pg.GraphicsView()
        self.verticalLayout_123.addWidget(self.pw)
        l = pg.GraphicsLayout()
        self.pw.setCentralWidget(l)
        l.addItem(a_3, row=2, col=3, rowspan=1, colspan=1)      
        l.addItem(a_2, row=2, col=1, rowspan=1, colspan=1)
        self.pI = pg.PlotItem()
        self.v_1 = self.pI.vb
        l.addItem(self.pI, row=2, col=2, rowspan=1, colspan=1)
        self.v_2 = pg.ViewBox()
        self.v_3 = pg.ViewBox()
        l.scene().addItem(self.v_2)
        l.scene().addItem(self.v_3)

        a_2.linkToView(self.v_2)
        a_3.linkToView(self.v_3)

        self.v_1.setRange(xRange=[-3599, 0])
        self.v_1.setLimits(xMax=0)

        self.v_2.setXLink(self.v_1)
        self.v_3.setXLink(self.v_2)

        self.pI.getAxis("left").setLabel('相机', color='red')
        a_2.setLabel('更新', color='green')
        a_3.setLabel('预测', color='blue')

        self.v_1.sigResized.connect(self.updateViews)

        self.v_1.enableAutoRange('y', 0.95)
        self.v_2.enableAutoRange('y', 0.95)
        self.v_3.enableAutoRange('y', 0.95)

        self.p1 = pg.PlotDataItem()      
        self.p1.setPen((255, 0, 0))
        self.v_1.addItem(self.p1)
        self.p2 = pg.PlotDataItem() 
        self.p2.setPen((0, 255, 0))
        self.v_2.addItem(self.p2)
        self.p3 = pg.PlotDataItem() 
        self.p3.setPen((0, 0, 255))
        self.v_3.addItem(self.p3)
        
        self.pw_x = pg.PlotWidget(name='Plotx')
        self.pw_y = pg.PlotWidget(name='Ploty')
        self.pw_z = pg.PlotWidget(name='Plotz')


        self.verticalLayout_xyz.addWidget(self.pw_x)
        self.verticalLayout_xyz.addWidget(self.pw_y)
        self.verticalLayout_xyz.addWidget(self.pw_z)

        self.pw_x.setLabel('left', 'angle', units='°')
        self.pw_x.setLabel('bottom', 'time', units='s')
        self.pw_y.setLabel('left', 'angle', units='°')
        self.pw_y.setLabel('bottom', 'time', units='s')
        self.pw_z.setLabel('left', 'angle', units='°')
        self.pw_z.setLabel('bottom', 'time', units='s')
        self.pw_x.setRange(xRange=[-3599, 0], yRange=[-180,180])
        self.pw_x.setLimits(xMax=0)
        self.pw_y.setRange(xRange=[-3599, 0], yRange=[-180,180])
        self.pw_y.setLimits(xMax=0)
        self.pw_z.setRange(xRange=[-3599, 0], yRange=[-180,180])
        self.pw_z.setLimits(xMax=0)

        self.pw_x.setLabel(
            'top', "<span style='font-size: 12pt'> pitch </span>")

        self.pw_y.setLabel(
            'top', "<span style='font-size: 12pt'> yaw </span>")

        self.pw_z.setLabel(
            'top', "<span style='font-size: 12pt'> roll </span>")
            
        self.p1_x = self.pw_x.plot()
        self.p1_x.setPen((255, 0, 0))
        self.p2_x = self.pw_x.plot()
        self.p2_x.setPen((0, 255, 0))
        self.p3_x = self.pw_x.plot()
        self.p3_x.setPen((0, 0, 255))

        self.p1_y = self.pw_y.plot()
        self.p1_y.setPen((255, 0, 0))
        self.p2_y = self.pw_y.plot()
        self.p2_y.setPen((0, 255, 0))
        self.p3_y = self.pw_y.plot()
        self.p3_y.setPen((0, 0, 255))

        self.p1_z = self.pw_z.plot()
        self.p1_z.setPen((255, 0, 0))
        self.p2_z = self.pw_z.plot()
        self.p2_z.setPen((0, 255, 0))
        self.p3_z = self.pw_z.plot()
        self.p3_z.setPen((0, 0, 255))

        # proxy_1 = pg.SignalProxy(self.v_1.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)
        # proxy_2 = pg.SignalProxy(self.pw_2.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)
        # proxy_3 = pg.SignalProxy(self.pw_3.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)
        # proxy_x = pg.SignalProxy(self.pw_x.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)
        # proxy_y = pg.SignalProxy(self.pw_y.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)
        # proxy_z = pg.SignalProxy(self.pw_z.scene().sigMouseMoved,
        #                        rateLimit=60, slot=self.mouseMoved)

        color = QColor(0, 255, 0)
        # self.label.setScaledContents(True)
        self.pushButton.setStyleSheet('QWidget{background-color:%s}'%color.name())
        self.pushButton.setText("接收数据")
        self.stop = False
        # self.tab_2 = QtWidgets.QWidget(EmbTerminal())
        # self.verticalLayout_3.addWidget(EmbTerminal())
        # self.verticalLayout_3.addWidget(EmbTerminal_2())
        # self.tabWidget.addTab(EmbTerminal(), "EmbTerminal")

    def updateViews(self):
        self.v_2.setGeometry(self.v_1.sceneBoundingRect())
        self.v_3.setGeometry(self.v_2.sceneBoundingRect())
    
    # def updateDelay(self, x, y1, y2, y3):
    #     self.v_1.addItem()

    def openCam(self, s):
        os.system(
            "gnome-terminal -e 'bash -c \"roslaunch imu_tty pnp_imu.launch; exec bash\"'")

    def openImu(self, s):
        os.system(
            "gnome-terminal -e 'bash -c \"roslaunch msf_updates viconpos_sensor.launch; exec bash\"'")

    def startRecv(self):
        if not hasattr(self, "recv"):
            self.recv = RecvData()
            self.recvThread = threading.Thread(target=self.update)
            self.recvThread.start()
            color = QColor(255, 0, 0)
            self.pushButton.setStyleSheet('QWidget{background-color:%s}'%color.name())
            self.pushButton.setText("停止接收数据")
        elif self.recv.isRun():
            self.recv.stop()
            # self.recvThread.join()
            color = QColor(0, 255, 0)
            self.pushButton.setStyleSheet('QWidget{background-color:%s}'%color.name())
            self.pushButton.setText("接收数据")

        else:
            # self.recvThread = threading.Thread(target=self.update)
            # self.recvThread.start()
            self.recv.start()
            color = QColor(255, 0, 0)
            self.pushButton.setStyleSheet('QWidget{background-color:%s}'%color.name())
            self.pushButton.setText("停止接收数据")
            


    def update(self):
        while not self.stop:
            # 接收数据
            data = self.recv.getData()
            image = self.recv.getImage()
            if image is not None:
                convertToQtFormat = QtGui.QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio)
                self.label.setPixmap(QPixmap.fromImage(p))
                # cv2.imshow("image", image)
                # cv2.waitKey(1)
                # print(self.label.size())
            if data is not None:
                for key in DICT_NAME_LIST:
                    self.lsts[key].append(data[key])
                    while len(self.lsts[key]) > 3600:
                        self.lsts[key].pop(0)
                # print(data)
            else:
                continue
            
            # 绘图
            # fps类
            x = list(range(-3599, 1))
            y1 = self.lsts["DT_BY_CAM"]
            y2 = self.lsts["DT_BY_UPDATE"]
            y3 = self.lsts["DT_BY_PRE"]
            self.p1.setData(x=x, y=y1)
            self.p2.setData(x=x, y=y2)
            self.p3.setData(x=x, y=y3)
            # 坐标类
            # c0 = np.array([10.0, 0.0, 0.0])
            # c1 = np.dot(c0, self.quaternion_to_rotation_matrix(
            #     self.lsts["ANGLE_BY_CAM"][-1]))
            # c2 = np.dot(c0, self.quaternion_to_rotation_matrix(
            #     self.lsts["ANGLE_BY_UPDATE"][-1]))
            # c3 = np.dot(c0, self.quaternion_to_rotation_matrix(
            #     self.lsts["ANGLE_BY_PRE"][-1]))
            # self.m1.resetTransform()
            # self.m2.resetTransform()
            # self.m3.resetTransform()
            # self.m1.translate(c1[0], c1[1], c1[2])
            # self.m2.translate(c2[0], c2[1], c2[2])
            # self.m3.translate(c3[0], c3[1], c3[2])
            # 角度类
            y1 = self.lsts["EUL_BY_CAM_X"]
            y2 = self.lsts["EUL_BY_UPDATE_X"]
            y3 = self.lsts["EUL_BY_PRE_X"]
            self.p1_x.setData(x=x, y=y1)
            self.p2_x.setData(x=x, y=y2)
            self.p3_x.setData(x=x, y=y3)

            y1 = self.lsts["EUL_BY_CAM_Y"]
            y2 = self.lsts["EUL_BY_UPDATE_Y"]
            y3 = self.lsts["EUL_BY_PRE_Y"]
            self.p1_y.setData(x=x, y=y1)
            self.p2_y.setData(x=x, y=y2)
            self.p3_y.setData(x=x, y=y3)
            
            y1 = self.lsts["EUL_BY_CAM_Z"]
            y2 = self.lsts["EUL_BY_UPDATE_Z"]
            y3 = self.lsts["EUL_BY_PRE_Z"]
            self.p1_z.setData(x=x, y=y1)
            self.p2_z.setData(x=x, y=y2)
            self.p3_z.setData(x=x, y=y3)
            # 直接输出类
            # eul = self.qua2eul(self.lsts["ANGLE_BY_PRE"][-1])
            s = "x:%0.1f, y:%0.1f, z:%0.1f；    pitch:%0.1f, yaw:%0.1f, roll:%0.1f" % (
                self.lsts["POSE_BY_PRE"][-1][0], self.lsts["POSE_BY_PRE"][-1][1], self.lsts["POSE_BY_PRE"][-1][2],
                self.lsts["EUL_BY_PRE_X"][-1], self.lsts["EUL_BY_PRE_Y"][-1], self.lsts["EUL_BY_PRE_Z"][-1])
            self.listWidget.insertItem(0, s)
            s = s + " 阈值:%s" % self.lsts["THRESOLD"][-1]
            self.statusbar.showMessage(s)
            # print(s)

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

    def quaternion_to_rotation_matrix(self, qua):
        q = np.array(qua)
        n = np.dot(q, q)
        if n < np.finfo(q.dtype).eps:
            return np.identity(3)
        q = q * np.sqrt(2.0 / n)
        q = np.outer(q, q)
        rot_matrix = np.array(
            [[1.0 - q[2, 2] - q[3, 3], q[1, 2] + q[3, 0], q[1, 3] - q[2, 0]],
             [q[1, 2] - q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] + q[1, 0]],
             [q[1, 3] + q[2, 0], q[2, 3] - q[1, 0], 1.0 - q[1, 1] - q[2, 2]]],
            dtype=q.dtype)
        return rot_matrix

    def mouseMoved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        print(index)
        if self.v_1.sceneBoundingRect().contains(pos):
            vb = self.v_1.vb
            mousePoint = vb.mapSceneToView(pos)
            print(index)
            index = int(mousePoint.x())
            if index > 0 and index < 3600:
                self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" %
                                   (mousePoint.x(), 0.1, 0.1))
            # self.vLine.setPos(mousePoint.x())
            # self.hLine.setPos(mousePoint.y())

    def closeEvent(self, event):
        self.recv.stop()
        self.stop = True
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    # window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
