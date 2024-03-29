# -*- coding: utf-8 -*-
import sys
import socket
import csv
from ui.Ui_gui import Ui_MainWindow
from ui.Ui_bagset import Ui_Dialog
from ui.Ui_setting import Ui_Dialog as Ui_Dialog_set
from ui.Ui_zttask import Ui_dialog as Ui_Dialog_zt
from ztUsage import ztUsage
from virtual_cam import virtualCAMDialog
import yaml
# from zt902e1 import ztScheduler, ztTask
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTabWidget, QMainWindow, QMessageBox, QTableWidgetItem, QAction, QDialog
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QProcess
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QIcon
from PyQt5.QtWidgets import QLabel, QWidget
import numpy as np
import pyqtgraph as pg
from recvData import RecvData
from sshCtl import sshCtl
from plotCamera import PlotCamera
from config import TIME_LENGTH
from analysis import analysisDialog
from camera_calibrate import camviewDialog
from recvIMU import RecvIMU
import threading
import time
import math
import os
import pyqtgraph.opengl as gl
import cv2
import queue
from router_graph import GraphicScene
from router_graph import GraphicView


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


TK_DICT_NAME_LIST = ["x_ang", "z_ang"]
TK_DICT_TYPE_LIST = [0.0, 0]
DICT_NAME_LIST = ["POSE_BY_CAM",  "ANGLE_BY_CAM", "DT_BY_CAM",
                  "POSE_BY_UPDATE", "ANGLE_BY_UPDATE", "DT_BY_UPDATE",
                  "POSE_BY_PRE", "ANGLE_BY_PRE", "DT_BY_PRE",
                  "DT_OF_FRAME", "THRESOLD", "COST_OF_IMG", "COST_OF_PRE", "COST_OF_UPDT",
                  "ANGLE_BY_IMU", "ANGLE_BY_INTEGRAL",
                  "EUL_BY_IMU_X", "EUL_BY_IMU_Y", "EUL_BY_IMU_Z",
                  "EUL_BY_CAM_X", "EUL_BY_UPDATE_X", "EUL_BY_PRE_X",
                  "EUL_BY_CAM_Y", "EUL_BY_UPDATE_Y", "EUL_BY_PRE_Y",
                  "EUL_BY_CAM_Z", "EUL_BY_UPDATE_Z", "EUL_BY_PRE_Z",
                  "EUL_BY_INTEGRAL_X", "EUL_BY_INTEGRAL_Y", "EUL_BY_INTEGRAL_Z",
                  "EUL_BY_STABLE_X", "EUL_BY_STABLE_Y", "EUL_BY_STABLE_Z",
                  "ANGLE_VELOCITY_X", "ANGLE_VELOCITY_Y", "ANGLE_VELOCITY_Z"]
DICT_TYPE_LIST = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], 0.0,
                  0.0, 0.0, 0, 0.0, 0.0,
                  [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0],
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0,
                  0.0, 0, 0.0]


class mywindow(QMainWindow, Ui_MainWindow):  # 这个窗口继承了用QtDesignner 绘制的窗口

    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.lsts = {}
        self.tk_lsts = {}
        self.zx_lsts = {}
        index = 0
        self.que = queue.Queue(1024)
        self.cond = threading.Condition()
        self.camera = PlotCamera(self.verticalLayout_camera)
        self.vins_ip = "192.168.50.69"
        self.vins_ssh_port = 22
        self.vins_user_name = "kylin"
        self.vins_user_key = "123123"
        self.vins_bin_path = "/home/kylin/zntk/bin/"
        self.save_enable = False
        with open("./config/zntkgui.yml",  encoding='utf-8') as f:
            yaml_cfg = yaml.load(f, Loader=yaml.FullLoader)
            self.vins_ip = yaml_cfg.get("vins_ip", self.vins_ip)
            self.vins_ssh_port = yaml_cfg.get("vins_ssh_port", self.vins_ssh_port)
            self.vins_user_name = yaml_cfg.get("vins_user_name", self.vins_user_name)
            self.vins_user_key = yaml_cfg.get("vins_user_key", self.vins_user_key)
            self.vins_bin_path = yaml_cfg.get("vins_bin_path", self.vins_bin_path)
            self.save_enable = yaml_cfg.get("save_enable", self.save_enable)
        self.ssh = sshCtl(command='cd ' + self.vins_bin_path,
                          host=self.vins_ip,
                          username=self.vins_user_name,
                          password=self.vins_user_key,
                          port=self.vins_ssh_port)
        self.ssh_trans = sshCtl(command='cd ' + self.vins_bin_path,
                          host=self.vins_ip,
                          username=self.vins_user_name,
                          password=self.vins_user_key,
                          port=self.vins_ssh_port)
        self.last_dct = {}
        self.zero_lsts = {}
        for key in DICT_NAME_LIST:
            self.lsts[key] = [DICT_TYPE_LIST[index]] * TIME_LENGTH
            self.last_dct[key] = DICT_TYPE_LIST[index]
            self.zero_lsts[key] = DICT_TYPE_LIST[index]
            index = index + 1
        index = 0
        self.last_tk_dct = {}
        self.zero_tk_dct = {}
        for key in TK_DICT_NAME_LIST:
            self.tk_lsts[key] = [TK_DICT_TYPE_LIST[index]] * TIME_LENGTH
            self.last_tk_dct[key] = TK_DICT_TYPE_LIST[index]
            self.zero_tk_dct[key] = TK_DICT_TYPE_LIST[index]
            index = index + 1
        index = 0
        self.last_zx_dct = {}
        self.zero_zx_dct = {}
        for key in TK_DICT_NAME_LIST:
            self.zx_lsts[key] = [TK_DICT_TYPE_LIST[index]] * TIME_LENGTH
            self.last_zx_dct[key] = TK_DICT_TYPE_LIST[index]
            self.zero_zx_dct[key] = TK_DICT_TYPE_LIST[index]
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

        self.v_1.setRange(xRange=[1 - TIME_LENGTH, 0])
        self.v_1.setLimits(xMax=0)

        self.v_2.setXLink(self.v_1)
        self.v_3.setXLink(self.v_2)

        self.pI.getAxis("left").setLabel('视觉', color='red')
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
        self.p3.setPen((255, 255, 255))
        self.v_3.addItem(self.p3)
        self.p4 = pg.PlotDataItem()
        self.p4.setPen((128, 128, 128))
        self.v_3.addItem(self.p4)

        self.pw_x = pg.PlotWidget(name='Plotx',_callSync='off')
        self.pw_y = pg.PlotWidget(name='Ploty',_callSync='off')
        self.pw_z = pg.PlotWidget(name='Plotz',_callSync='off')

        self.verticalLayout_xyz.addWidget(self.pw_x)
        self.verticalLayout_xyz.addWidget(self.pw_y)
        self.verticalLayout_xyz.addWidget(self.pw_z)

        self.pw_x.setLabel('left', 'angle', units='°')
        self.pw_x.setLabel('bottom', 'time', units='s')
        self.pw_y.setLabel('left', 'angle', units='°')
        self.pw_y.setLabel('bottom', 'time', units='s')
        self.pw_z.setLabel('left', 'angle', units='°')
        self.pw_z.setLabel('bottom', 'time', units='s')
        self.pw_x.setRange(xRange=[1 - TIME_LENGTH, 0], yRange=[-180, 180])
        self.pw_x.setLimits(xMax=0)
        self.pw_y.setRange(xRange=[1 - TIME_LENGTH, 0], yRange=[-180, 180])
        self.pw_y.setLimits(xMax=0)
        self.pw_z.setRange(xRange=[1 - TIME_LENGTH, 0], yRange=[-180, 180])
        self.pw_z.setLimits(xMax=0)

        self.pw_x.setLabel(
            'top', "<span style='font-size: 12pt'> pitch </span>")

        self.pw_y.setLabel(
            'top', "<span style='font-size: 12pt'> yaw </span>")

        self.pw_z.setLabel(
            'top', "<span style='font-size: 12pt'> roll </span>")

        self.p1_x = self.pw_x.plot(_callSync='off')
        self.p1_x.setPen((255, 0, 0))
        self.p2_x = self.pw_x.plot(_callSync='off')
        self.p2_x.setPen((0, 255, 0))
        self.p3_x = self.pw_x.plot(_callSync='off')
        self.p3_x.setPen((255, 255, 255))
        self.p4_x = self.pw_x.plot(_callSync='off')
        self.p4_x.setPen((0, 0, 255))
        self.p5_x = self.pw_x.plot(_callSync='off')
        self.p5_x.setPen((128, 128, 128))
        self.p6_x = self.pw_x.plot(_callSync='off')
        self.p6_x.setPen(color=(255, 255, 0), style=QtCore.Qt.DashLine)
        self.p7_x = self.pw_x.plot(_callSync='off')
        self.p7_x.setPen((212, 35, 122))
        self.p8_x = self.pw_x.plot(_callSync='off')
        self.p8_x.setPen((19, 34, 122))
        self.p_angle_velocity_x = self.pw_x.plot(_callSync='off')
        self.p_angle_velocity_x.setPen((19, 34, 122), style=QtCore.Qt.DashLine)

        self.p1_y = self.pw_y.plot(_callSync='off')
        self.p1_y.setPen((255, 0, 0))
        self.p2_y = self.pw_y.plot(_callSync='off')
        self.p2_y.setPen((0, 255, 0))
        self.p3_y = self.pw_y.plot(_callSync='off')
        self.p3_y.setPen((255, 255, 255))
        self.p4_y = self.pw_y.plot(_callSync='off')
        self.p4_y.setPen((0, 0, 255))
        self.p5_y = self.pw_y.plot(_callSync='off')
        self.p5_y.setPen((128, 128, 128))
        self.p6_y = self.pw_y.plot(_callSync='off')
        self.p6_y.setPen(color=(255, 255, 0), style=QtCore.Qt.DashLine)
        self.p7_y = self.pw_y.plot(_callSync='off')
        self.p7_y.setPen((212, 35, 122))
        self.p8_y = self.pw_y.plot(_callSync='off')
        self.p8_y.setPen((19, 34, 122))
        self.p_angle_velocity_y = self.pw_y.plot(_callSync='off')
        self.p_angle_velocity_y.setPen((19, 34, 122), style=QtCore.Qt.DashLine)

        self.p1_z = self.pw_z.plot(_callSync='off')
        self.p1_z.setPen((255, 0, 0))
        self.p2_z = self.pw_z.plot(_callSync='off')
        self.p2_z.setPen((0, 255, 0))
        self.p3_z = self.pw_z.plot(_callSync='off')
        self.p3_z.setPen((255, 255, 255))
        self.p4_z = self.pw_z.plot(_callSync='off')
        self.p4_z.setPen((0, 0, 255))
        self.p5_z = self.pw_z.plot(_callSync='off')
        self.p5_z.setPen((128, 128, 128))
        self.p6_z = self.pw_z.plot(_callSync='off')
        self.p6_z.setPen(color=(255, 255, 0), style=QtCore.Qt.DashLine)
        self.p7_z = self.pw_z.plot(_callSync='off')
        self.p7_z.setPen((212, 35, 122))
        self.p8_z = self.pw_z.plot(_callSync='off')
        self.p8_z.setPen((19, 34, 122))
        self.p_angle_velocity_z = self.pw_z.plot(_callSync='off')
        self.p_angle_velocity_z.setPen((19, 34, 122), style=QtCore.Qt.DashLine)

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

        # self.label.setScaledContents(True)

        self.toolBtnStart = QAction(QIcon('./res/播放.png'), '开始', self)
        self.toolBtnStart.triggered.connect(self.startRecv)
        self.toolBtnStart.setShortcut('Space')

        self.toolBtnConnect = QAction(QIcon('./res/连接.png'), '远程连接', self)
        self.toolBtnConnect.triggered.connect(self.connect)
        self.toolBtnConnect.setEnabled(False)
        self.toolBtnConnect.setShortcut('Ctrl+N')

        self.toolBtnTrans = QAction(QIcon('./res/透传.png'), '转台透传', self)
        self.toolBtnTrans.triggered.connect(self.connectTrans)
        self.toolBtnTrans.setEnabled(False)

        self.toolBtnNormal = QAction(QIcon('./res/加速.png'), '正常运行', self)
        self.toolBtnNormal.triggered.connect(self.normalRun)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnNormal.setShortcut('Ctrl+1')

        self.toolBtnRecord = QAction(QIcon('./res/录音.png'), '录包', self)
        self.toolBtnRecord.triggered.connect(self.recordBag)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnRecord.setShortcut('Ctrl+2')

        self.toolBtnPlay = QAction(QIcon('./res/喇叭.png'), '回放', self)
        self.toolBtnPlay.triggered.connect(self.playBag)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnPlay.setShortcut('Ctrl+3')

        self.toolBtnInit = QAction(QIcon('./res/相机.png'), '装车初始化', self)
        self.toolBtnInit.triggered.connect(self.initRun)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnInit.setShortcut('Ctrl+4')

        self.toolBtnIMUInit = QAction(QIcon('./res/指南针.png'), 'IMU初始化', self)
        self.toolBtnIMUInit.triggered.connect(self.initIMU)
        self.toolBtnIMUInit.setEnabled(False)
        self.toolBtnIMUInit.setShortcut('Ctrl+5')

        self.toolBtnReset = QAction(QIcon('./res/重播.png'), '重置', self)
        self.toolBtnReset.triggered.connect(self.resetRemote)
        self.toolBtnReset.setEnabled(False)
        self.toolBtnReset.setShortcut('Ctrl+R')

        self.toolBtnClose = QAction(QIcon('./res/关机.png'), '停止', self)
        self.toolBtnClose.triggered.connect(self.closeRemote)
        self.toolBtnClose.setEnabled(False)
        self.toolBtnReset.setShortcut('Ctrl+T')

        self.toolBtnSetting = QAction(QIcon('./res/设置.png'), '设置', self)
        self.toolBtnSetting.triggered.connect(self.settingSSH)
        self.toolBtnSetting.setEnabled(True)

        self.redON = False
        self.greenON = False
        self.blueON = True
        self.imuON = False
        self.intON = False
        self.stableON = False
        self.anglevON = False
        self.clZTON =False
        self.zxZTON =False

        self.toolBtnViewRed = QAction(QIcon('./res/过滤红.png'), '视觉', self)
        self.toolBtnViewRed.triggered.connect(self.toggleRed)
        self.toolBtnViewRed.setEnabled(True)

        self.toolBtnViewGreen = QAction(QIcon('./res/过滤绿.png'), '更新', self)
        self.toolBtnViewGreen.triggered.connect(self.toggleGreen)
        self.toolBtnViewGreen.setEnabled(True)

        self.toolBtnViewBlue = QAction(QIcon('./res/过滤白.png'), '预测', self)
        self.toolBtnViewBlue.triggered.connect(self.toggleBlue)
        self.toolBtnViewBlue.setEnabled(True)

        self.toolBtnViewIMU = QAction(QIcon('./res/过滤蓝.png'), '纯IMU', self)
        self.toolBtnViewIMU.triggered.connect(self.toggleIMU)
        self.toolBtnViewIMU.setEnabled(True)

        self.toolBtnViewINT = QAction(QIcon('./res/过滤粉.png'), '差分积分', self)
        self.toolBtnViewINT.triggered.connect(self.toggleINT)
        self.toolBtnViewINT.setEnabled(True)

        self.toolBtnViewSTABLE = QAction(QIcon('./res/过滤-深蓝.png'), '自稳输出', self)
        self.toolBtnViewSTABLE.triggered.connect(self.toggleSTABLE)
        self.toolBtnViewSTABLE.setEnabled(True)

        self.toolBtnViewANGLEV = QAction(QIcon('./res/过滤-深蓝.png'), '自稳输出', self)
        self.toolBtnViewANGLEV.triggered.connect(self.toggleANGLEV)
        self.toolBtnViewANGLEV.setEnabled(True)

        self.toolBtnViewCLZT = QAction(QIcon('./res/过滤灰.png'), '测量转台', self)
        self.toolBtnViewCLZT.triggered.connect(self.toggleCLZT)
        self.toolBtnViewCLZT.setEnabled(True)

        self.toolBtnViewZXZT = QAction(QIcon('./res/过滤灰.png'), '执行转台', self)
        self.toolBtnViewZXZT.triggered.connect(self.toggleZXZT)
        self.toolBtnViewZXZT.setEnabled(True)

        self.toolBtnClearChart = QAction(QIcon('./res/删除.png'), '清空', self)
        self.toolBtnClearChart.triggered.connect(self.clearChart)
        self.toolBtnClearChart.setEnabled(True)

        self.toolBtnAlign = QAction(QIcon('./res/对齐.png'), '对齐一次', self)
        self.toolBtnAlign.triggered.connect(self.alignOnce)
        self.toolBtnAlign.setEnabled(True)

        self.toolBtnZTDialog = QAction(QIcon('./res/virtual.png'), '仿真', self)
        self.toolBtnZTDialog.triggered.connect(self.settingZT)
        self.toolBtnZTDialog.setEnabled(True)

        self.toolBtnAnalysisDialog = QAction(QIcon('./res/数据.png'), '分析数据', self)
        self.toolBtnAnalysisDialog.triggered.connect(self.analysis)
        self.toolBtnAnalysisDialog.setEnabled(True)

        self.toolBtnCameraCalibrateDialog = QAction(QIcon('./res/棋盘.png'), '本机相机标定', self)
        self.toolBtnCameraCalibrateDialog.triggered.connect(self.camearCalibrate)
        self.toolBtnCameraCalibrateDialog.setEnabled(True)

        

        self.toolBar.addAction(self.toolBtnStart)
        self.toolBar.addAction(self.toolBtnConnect)
        self.toolBar.addAction(self.toolBtnTrans)
        self.toolbar_2 = self.addToolBar('模式')
        self.toolbar_2.addAction(self.toolBtnNormal)
        self.toolbar_2.addAction(self.toolBtnRecord)
        self.toolbar_2.addAction(self.toolBtnPlay)
        self.toolbar_2.addAction(self.toolBtnIMUInit)
        self.toolbar_2.addAction(self.toolBtnInit)

        self.toolbar_3 = self.addToolBar('控制')
        self.toolbar_3.addAction(self.toolBtnReset)
        self.toolbar_3.addAction(self.toolBtnClose)

        self.toolbar_4 = self.addToolBar('设置')
        self.toolbar_4.addAction(self.toolBtnSetting)

        self.toolbar_5 = self.addToolBar('折线')
        self.toolbar_5.addAction(self.toolBtnAlign)
        self.toolbar_5.addAction(self.toolBtnViewRed)
        self.toolbar_5.addAction(self.toolBtnViewGreen)
        self.toolbar_5.addAction(self.toolBtnViewBlue)
        self.toolbar_5.addAction(self.toolBtnViewIMU)
        self.toolbar_5.addAction(self.toolBtnViewINT)
        self.toolbar_5.addAction(self.toolBtnViewSTABLE)
        self.toolbar_5.addAction(self.toolBtnViewCLZT)
        self.toolbar_5.addAction(self.toolBtnViewZXZT)
        self.toolbar_5.addAction(self.toolBtnClearChart)

        self.toolbar_6 = self.addToolBar('转台')
        self.toolbar_6.addAction(self.toolBtnZTDialog)
        self.toolbar_6.addAction(self.toolBtnAnalysisDialog)
        self.toolbar_6.addAction(self.toolBtnCameraCalibrateDialog)


        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar_3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar_4.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar_5.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar_6.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # self.setWindowOpacity(0.9)  # 设置窗口透明度
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.stop = False

        self.timer = QTimer()
        self.ztresave = threading.Event()
        self.zxresave = threading.Event()
        self.camera.add_pose([0, 0, 0], [0.0, 0.0, 0.0, 1.0])
        # self.tab_2 = QtWidgets.QWidget(EmbTerminal())
        # self.verticalLayout_3.addWidget(EmbTerminal())
        # self.verticalLayout_3.addWidget(EmbTerminal_2())
        # self.tabWidget.addTab(EmbTerminal(), "EmbTerminal")

        self.router_sence = GraphicScene(self.graphicsView)
        self.router_view = GraphicView(self.router_sence, self.graphicsView, self.vins_ip)

        self.showMaximized()
        
    def alignOnce(self):
        for key in DICT_NAME_LIST:
            self.zero_lsts[key] = self.lsts[key][-1]
        for key in TK_DICT_NAME_LIST:
            self.zero_tk_dct[key] = self.tk_lsts[key][-1]
            self.zero_zx_dct[key] = self.zx_lsts[key][-1]

    def clearChart(self):
        index = 0
        for key in DICT_NAME_LIST:
            self.lsts[key] = [DICT_TYPE_LIST[index]] * TIME_LENGTH
            index = index + 1
        index = 0
        for key in TK_DICT_NAME_LIST:
            self.tk_lsts[key] = [TK_DICT_TYPE_LIST[index]] * TIME_LENGTH
            self.zx_lsts[key] = [TK_DICT_TYPE_LIST[index]] * TIME_LENGTH
            index = index + 1
        x = list(range(1 - TIME_LENGTH, 1))
        y1 = self.lsts["DT_BY_CAM"]
        self.p1.setData(x=x, y=y1)
        y2 = self.lsts["DT_BY_UPDATE"]
        self.p2.setData(x=x, y=y2)
        y3 = self.lsts["DT_BY_PRE"]            
        self.p3.setData(x=x, y=y3)
        # 角度类
        y1 = self.lsts["EUL_BY_CAM_X"]
        self.p1_x.setData(x=x, y=y1)
        y2 = self.lsts["EUL_BY_UPDATE_X"]
        self.p2_x.setData(x=x, y=y2)
        y3 = self.lsts["EUL_BY_PRE_X"]            
        self.p3_x.setData(x=x, y=y3)
        y4 = self.lsts["EUL_BY_IMU_X"]            
        self.p4_x.setData(x=x, y=y4)
        y5 = self.tk_lsts["x_ang"]
        self.p5_x.setData(x=x, y=y5)
        y6 = self.zx_lsts["x_ang"]
        self.p6_x.setData(x=x, y=y6)
        y7 = self.lsts["EUL_BY_INTEGRAL_X"]
        self.p7_x.setData(x=x, y=y7)

        y1 = self.lsts["EUL_BY_CAM_Y"]
        self.p1_y.setData(x=x, y=y1)
        y2 = self.lsts["EUL_BY_UPDATE_Y"]
        self.p2_y.setData(x=x, y=y2)
        y3 = self.lsts["EUL_BY_PRE_Y"]            
        self.p3_y.setData(x=x, y=y3)
        y4 = self.lsts["EUL_BY_IMU_Y"]            
        self.p4_y.setData(x=x, y=y4)
        # y5 = self.tk_lsts["z_ang"]
        # self.p5_y.setData(x=x, y=y5)
        # y6 = self.zx_lsts["z_ang"]
        # self.p6_y.setData(x=x, y=y6)
        y7 = self.lsts["EUL_BY_INTEGRAL_Y"]
        self.p7_y.setData(x=x, y=y7)

        y1 = self.lsts["EUL_BY_CAM_Z"]
        self.p1_z.setData(x=x, y=y1)
        y2 = self.lsts["EUL_BY_UPDATE_Z"]
        self.p2_z.setData(x=x, y=y2)
        y3 = self.lsts["EUL_BY_PRE_Z"]            
        self.p3_z.setData(x=x, y=y3)
        y4 = self.lsts["EUL_BY_IMU_Z"]            
        self.p4_z.setData(x=x, y=y4)
        y5 = self.tk_lsts["z_ang"]
        self.p5_z.setData(x=x, y=y5)
        y6 = self.zx_lsts["z_ang"]
        self.p6_z.setData(x=x, y=y6)
        y7 = self.lsts["EUL_BY_INTEGRAL_Z"]
        self.p7_z.setData(x=x, y=y7)

    def toggleRed(self):
        self.redON = not(self.redON)
        self.reflash()
        if self.redON:
            self.toolBtnViewRed.setIcon(QIcon('./res/过滤红.png'))
        else:
            self.toolBtnViewRed.setIcon(QIcon('./res/过滤关.png'))

    def toggleGreen(self):
        self.greenON = not(self.greenON)
        self.reflash()
        if self.greenON:
            self.toolBtnViewGreen.setIcon(QIcon('./res/过滤绿.png'))
        else:
            self.toolBtnViewGreen.setIcon(QIcon('./res/过滤关.png'))

    def toggleBlue(self):
        self.blueON = not(self.blueON)
        self.reflash()
        if self.blueON:
            self.toolBtnViewBlue.setIcon(QIcon('./res/过滤白.png'))
        else:
            self.toolBtnViewBlue.setIcon(QIcon('./res/过滤关.png'))

    def toggleANGLEV(self):
        self.anglevON = not(self.anglevON)
        self.reflash()
        if self.anglevON:
            self.toolBtnViewANGLEV.setIcon(QIcon('./res/过滤-深蓝.png'))
        else:
            self.toolBtnViewANGLEV.setIcon(QIcon('./res/过滤关.png'))

    def toggleSTABLE(self):
        self.stableON = not(self.stableON)
        self.reflash()
        if self.stableON:
            self.toolBtnViewSTABLE.setIcon(QIcon('./res/过滤-深蓝.png'))
        else:
            self.toolBtnViewSTABLE.setIcon(QIcon('./res/过滤关.png'))

    def toggleINT(self):
        self.intON = not(self.intON)
        self.reflash()
        if self.intON:
            self.toolBtnViewINT.setIcon(QIcon('./res/过滤粉.png'))
        else:
            self.toolBtnViewINT.setIcon(QIcon('./res/过滤关.png'))

    def toggleIMU(self):
        self.imuON = not(self.imuON)
        self.reflash()
        if self.imuON:
            self.toolBtnViewIMU.setIcon(QIcon('./res/过滤蓝.png'))
        else:
            self.toolBtnViewIMU.setIcon(QIcon('./res/过滤关.png'))

    def toggleCLZT(self):
        self.clZTON = not(self.clZTON)
        self.reflash()
        if self.clZTON:
            self.toolBtnViewCLZT.setIcon(QIcon('./res/过滤灰.png'))
        else:
            self.toolBtnViewCLZT.setIcon(QIcon('./res/过滤关.png'))

    def toggleZXZT(self):
        self.zxZTON = not(self.zxZTON)
        self.reflash()
        if self.zxZTON:
            self.toolBtnViewZXZT.setIcon(QIcon('./res/过滤灰.png'))
        else:
            self.toolBtnViewZXZT.setIcon(QIcon('./res/过滤关.png'))

    def camearCalibrate(self):
        dialog = camviewDialog()
        # dialog.show()
        if dialog.exec():
            pass

    def analysis(self):
        dialog = analysisDialog()
        dialog.show()
        # pass
        # if dialog.exec():
        #     return

    def settingZT(self):
        dialog = virtualCAMDialog()
        dialog.show()
        dialog.exec()
       

    def settingSSH(self):
        host = self.vins_ip
        port = self.vins_ssh_port
        username = self.vins_user_name
        password = self.vins_user_key
        return
        dialog = QDialog()
        setDialog = Ui_Dialog_set()
        setDialog.setupUi(dialog)
        if dialog.exec():
            host = setDialog.lineEdit.text()
            port = int(setDialog.spinBox.value())
            username = setDialog.lineEdit_3.text()
            password = setDialog.lineEdit_4.text()
        else:
            return
        self.ssh.setHost(host)
        self.ssh.setPort(port)
        self.ssh.setUsername(username)
        self.ssh.setPassword(password)

    def closeRemote(self):
        self.ssh.sendCommand('x')
        time.sleep(0.1)
        cvstrs = self.ssh.cbstrs
        
        self.recv.close_start()
        self.recvImu.pause = True
        self.recvZxzt.pause = True
        self.ztresave.set()
        self.zxresave.set()
        self.toolBtnReset.setEnabled(False)
        self.toolBtnClose.setEnabled(False)
        self.toolBtnPlay.setEnabled(True)
        self.toolBtnRecord.setEnabled(True)
        self.toolBtnNormal.setEnabled(True)
        self.toolBtnInit.setEnabled(True)
        self.toolBtnIMUInit.setEnabled(True)
        if len(cvstrs) > 0:
            s = "".join(cvstrs)
            s = s[s.find('--') : s.rfind('--')]
            msgBox = QMessageBox.information(self, "执行结束", s)
        self.ssh.startpushflag = False
        self.ssh.cbstrs.clear()

    def resetRemote(self):
        self.ssh.sendCommand('r')

    def initIMU(self):
        self.ssh.sendCommand(
            './imu_init')
        self.toolBtnReset.setEnabled(True)
        self.toolBtnClose.setEnabled(True)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnIMUInit.setEnabled(False)

    def normalRun(self):
        self.recvImu.pause = False
        self.recvZxzt.pause = False
        self.ssh.sendCommand(
            './zntk_core -b')
        self.toolBtnReset.setEnabled(True)
        self.toolBtnClose.setEnabled(True)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnIMUInit.setEnabled(False)

    def playBag(self):
        dialog = QDialog()
        bagsetDialog = Ui_Dialog()
        bagsetDialog.setupUi(dialog)
        bagname = 'temp'
        rate = 1.0
        if dialog.exec():
            bagname = bagsetDialog.lineEdit.text()
            rate = bagsetDialog.doubleSpinBox.value()
        else:
            return
        self.ssh.sendCommand(
            './zntk_core -b -p ' + bagname + ' -rate ' + str(rate))
        self.toolBtnReset.setEnabled(True)
        self.toolBtnClose.setEnabled(True)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnIMUInit.setEnabled(False)

    def recordBag(self):
        dialog = QDialog()
        bagsetDialog = Ui_Dialog()
        bagsetDialog.setupUi(dialog)
        bagsetDialog.doubleSpinBox.setEnabled(False)     
        bagname = 'temp'
        if dialog.exec():
            bagname = bagsetDialog.lineEdit.text()
        else:
            return
        self.ssh.sendCommand(
            './zntk_core -r ' + bagname)
        self.toolBtnReset.setEnabled(True)
        self.toolBtnClose.setEnabled(True)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnIMUInit.setEnabled(False)

    def initRun(self):
        self.ssh.sendCommand(
            './zntk_core -s')
        self.toolBtnReset.setEnabled(True)
        self.toolBtnClose.setEnabled(True)
        self.toolBtnPlay.setEnabled(False)
        self.toolBtnRecord.setEnabled(False)
        self.toolBtnNormal.setEnabled(False)
        self.toolBtnInit.setEnabled(False)
        self.toolBtnIMUInit.setEnabled(False)

    def connect(self):
        self.toolBtnPlay.setEnabled(True)
        self.toolBtnRecord.setEnabled(True)
        self.toolBtnNormal.setEnabled(True)
        self.toolBtnInit.setEnabled(True)
        self.toolBtnIMUInit.setEnabled(True)
        self.toolBtnConnect.setEnabled(False)
        self.toolBtnSetting.setEnabled(False)
        self.ssh.start()

    def connectTrans(self):
        self.toolBtnTrans.setEnabled(False)
        self.ssh_trans.start()
        time.sleep(1.0)
        self.ssh_trans.sendCommand('./zxzt_trans&')
        self.ssh_trans.sendCommand('./zt_trans&')

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
            self.recv = RecvData(enable_save=self.save_enable)
            self.recvImu = RecvIMU(usesock=True, socketPort=5580, saveName='_cl', save=True, event=self.ztresave)
            self.recvZxzt = RecvIMU(usesock=True, socketPort=5581, saveName='_zx', save=True, event=self.zxresave)
            # self.recvImu = RecvIMU(save=False)
            # self.recvThread = threading.Thread(target=self.update)
            # self.recvThread.start()
            self.timer.timeout.connect(self.update)
            self.timer.start(33)
            self.toolBtnStart.setIcon(QIcon('./res/暂停.png'))
            self.toolBtnStart.setText('暂停')
            self.toolBtnConnect.setEnabled(True)
            self.toolBtnTrans.setEnabled(True)
        elif self.recv.issend:
            self.recv.pause()
            self.recvImu.pause=True
            self.recvZxzt.pause=True
            self.toolBtnStart.setIcon(QIcon('./res/播放.png'))
            self.toolBtnStart.setText('恢复')
            # self.pushButton.setStyleSheet('QWidget{background-color:%s}'%color.name())
            # self.pushButton.setText("接收数据")
        else:
            self.recv.start()
            self.recvImu.pause=False
            self.recvZxzt.pause=False
            self.toolBtnStart.setIcon(QIcon('./res/暂停.png'))
            self.toolBtnStart.setText('暂停')

    def reflash(self):
        # 3D类
        self.camera.add_pose(self.lsts["POSE_BY_PRE"][-1], self.lsts["ANGLE_BY_PRE"][-1])
        self.camera.draw_history(self.lsts["POSE_BY_PRE"])
        # fps类
        x = list(range(1 - TIME_LENGTH, 1))
        if self.redON:
            y1 = self.lsts["DT_BY_CAM"]
            self.p1.setData(x=x, y=y1)
        if self.greenON:
            y2 = self.lsts["DT_BY_UPDATE"]
            self.p2.setData(x=x, y=y2)
        if self.blueON:
            y3 = self.lsts["DT_BY_PRE"]            
            self.p3.setData(x=x, y=y3)
        # 角度类
        if self.redON:
            y1 = self.lsts["EUL_BY_CAM_X"]
            self.p1_x.setData(x=x, y=y1)
        if self.greenON:
            y2 = self.lsts["EUL_BY_UPDATE_X"]
            self.p2_x.setData(x=x, y=y2)
        if self.blueON:
            y3 = self.lsts["EUL_BY_PRE_X"]            
            self.p3_x.setData(x=x, y=y3)
        if self.imuON:
            y4 = self.lsts["EUL_BY_IMU_X"]            
            self.p4_x.setData(x=x, y=y4)
        if self.clZTON:
            y5 = self.tk_lsts["x_ang"]
            self.p5_x.setData(x=x, y=y5)
        if self.zxZTON:
            y6 = self.zx_lsts["x_ang"]
            self.p6_x.setData(x=x, y=y6)
        if self.intON:
            y7 = self.lsts["EUL_BY_INTEGRAL_X"]
            self.p7_x.setData(x=x, y=y7)
        if self.stableON:
            y8 = self.lsts["EUL_BY_STABLE_X"]
            self.p8_x.setData(x=x, y=y8)
        if self.anglevON:
            y9 = self.lsts["ANGLE_VELOCITY_X"]
            self.p_angle_velocity_x.setData(x=x, y=y9)

        if self.redON:
            y1 = self.lsts["EUL_BY_CAM_Y"]
            self.p1_y.setData(x=x, y=y1)
        if self.greenON:
            y2 = self.lsts["EUL_BY_UPDATE_Y"]
            self.p2_y.setData(x=x, y=y2)
        if self.blueON:
            y3 = self.lsts["EUL_BY_PRE_Y"]            
            self.p3_y.setData(x=x, y=y3)
        if self.imuON:
            y4 = self.lsts["EUL_BY_IMU_Y"]            
            self.p4_y.setData(x=x, y=y4)
        # if self.clZTON:
        #     y5 = self.tk_lsts["z_ang"]
        #     self.p5_y.setData(x=x, y=y5)
        # if self.zxZTON:
        #     y6 = self.zx_lsts["z_ang"]
        #     self.p6_y.setData(x=x, y=y6)
        if self.intON:
            y7 = self.lsts["EUL_BY_INTEGRAL_Y"]
            self.p7_y.setData(x=x, y=y7)
        if self.stableON:
            y8 = self.lsts["EUL_BY_STABLE_Y"]
            self.p8_y.setData(x=x, y=y8)
        if self.anglevON:
            y9 = self.lsts["ANGLE_VELOCITY_Y"]
            self.p_angle_velocity_y.setData(x=x, y=y9)


        if self.redON:
            y1 = self.lsts["EUL_BY_CAM_Z"]
            self.p1_z.setData(x=x, y=y1)
        if self.greenON:
            y2 = self.lsts["EUL_BY_UPDATE_Z"]
            self.p2_z.setData(x=x, y=y2)
        if self.blueON:
            y3 = self.lsts["EUL_BY_PRE_Z"]            
            self.p3_z.setData(x=x, y=y3)
        if self.imuON:
            y4 = self.lsts["EUL_BY_IMU_Z"]            
            self.p4_z.setData(x=x, y=y4)
        if self.clZTON:
            y5 = self.tk_lsts["z_ang"]
            self.p5_z.setData(x=x, y=y5)
        if self.zxZTON:
            y6 = self.zx_lsts["z_ang"]
            self.p6_z.setData(x=x, y=y6)
        if self.intON:
            y7 = self.lsts["EUL_BY_INTEGRAL_Z"]
            self.p7_z.setData(x=x, y=y7)
        if self.stableON:
            y8 = self.lsts["EUL_BY_STABLE_Z"]
            self.p8_x.setData(x=x, y=y8)
        if self.anglevON:
            y9 = self.lsts["ANGLE_VELOCITY_Z"]
            self.p_angle_velocity_z.setData(x=x, y=y9)
        

        

    def update(self):
        if not self.stop:
            # 接收数据
            data = self.recv.getData()
            imudata = self.recvImu.getIMUdata()
            zxztdata = self.recvZxzt.getIMUdata()
            if data is not None and imudata is not None:
                for key in DICT_NAME_LIST:
                    self.lsts[key].append(data[key])
                    while len(self.lsts[key]) > TIME_LENGTH:
                        self.lsts[key].pop(0)
                self.last_dct = data.copy()
                for key in TK_DICT_NAME_LIST:
                    self.tk_lsts[key].append(imudata[key])
                    while len(self.tk_lsts[key]) > TIME_LENGTH:
                        self.tk_lsts[key].pop(0)
                self.last_tk_dct = imudata.copy()
            elif data is not None and imudata is None:
                for key in DICT_NAME_LIST:
                    self.lsts[key].append(data[key])
                    while len(self.lsts[key]) > TIME_LENGTH:
                        self.lsts[key].pop(0)
                self.last_dct = data.copy()
                for key in TK_DICT_NAME_LIST:
                    self.tk_lsts[key].append(self.last_tk_dct[key])
                    while len(self.tk_lsts[key]) > TIME_LENGTH:
                        self.tk_lsts[key].pop(0)
            elif data is None and imudata is not None:
                index = 0
                for key in DICT_NAME_LIST:
                    self.lsts[key].append(self.last_dct[key])
                    index = index + 1
                    while len(self.lsts[key]) > TIME_LENGTH:
                        self.lsts[key].pop(0)
                for key in TK_DICT_NAME_LIST:
                    self.tk_lsts[key].append(imudata[key])
                    while len(self.tk_lsts[key]) > TIME_LENGTH:
                        self.tk_lsts[key].pop(0)
                self.last_tk_dct = imudata.copy()
                # print(data)
            else:
                return
            
            for key in DICT_NAME_LIST:
                if isinstance(self.zero_lsts[key], list):
                    for i in range(len(self.zero_lsts[key])):
                        self.lsts[key][-1][i] = self.lsts[key][-1][i] - self.zero_lsts[key][i]
                else:
                    self.lsts[key][-1] = self.lsts[key][-1] - self.zero_lsts[key]
            for key in TK_DICT_NAME_LIST:
                self.tk_lsts[key][-1] = self.tk_lsts[key][-1] - self.zero_tk_dct[key]

            if zxztdata is not None:
                for key in TK_DICT_NAME_LIST:
                    self.zx_lsts[key].append(zxztdata[key] - self.zero_zx_dct[key])
                    while len(self.zx_lsts[key]) > TIME_LENGTH:
                        self.zx_lsts[key].pop(0)
                self.last_zx_dct = zxztdata.copy()

            if data is not None:
                # 绘图类
                image = np.zeros((400, 640, 3), np.uint8)
                for i in range(len(data["IMAGE_FEATURE_POINT_X"])):
                    cv2.circle(image,
                            (int(data["IMAGE_FEATURE_POINT_X"][i]),
                                int(data["IMAGE_FEATURE_POINT_Y"][i])),
                            10, (255, 255, 255), 3)
                convertToQtFormat = QtGui.QImage(
                    image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
                p = convertToQtFormat.scaled(
                    self.label.width(), self.label.height(), Qt.KeepAspectRatio)
                self.label.setPixmap(QPixmap.fromImage(p))
                
                # 直接输出类
                # eul = self.qua2eul(self.lsts["ANGLE_BY_PRE"][-1])
                s = "x:%0.1f, y:%0.1f, z:%0.1f；    pitch:%0.1f, yaw:%0.1f, roll:%0.1f" % (
                    self.lsts["POSE_BY_PRE"][-1][0], self.lsts["POSE_BY_PRE"][-1][1], self.lsts["POSE_BY_PRE"][-1][2],
                    self.lsts["EUL_BY_PRE_X"][-1], self.lsts["EUL_BY_PRE_Y"][-1], self.lsts["EUL_BY_PRE_Z"][-1])
                self.listWidget.insertItem(0, s)
                s = s + " 阈值:%s " % self.lsts["THRESOLD"][-1] + \
                    "共收到:%i" % self.recv.contsum + "包"
                self.statusbar.showMessage(s)
                # time.sleep(1.0 / 30.0)
                # print(s)
            self.reflash()

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

    def closeEvent(self, event):
        if hasattr(self, "recv"):
            self.recv.stop()
            self.recvImu.isRecv = False
            self.recvZxzt.isRecv = False
        if self.timer.isActive():
            self.timer.stop()
        self.ssh.isRun = False
        self.ssh_trans.isRun = False
        self.stop = True       
        event.accept()

    def save(self):
        headers = ['stamp', 'firstAxisPos', 'firstAxisVelocity', 'secondAxisPos', 'secondAxisVelocity']
        csv_name = './history/' + \
            str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '_zt.csv'
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
                    self.cond.release()
                if r is not None:
                    line = [(r["STAMP"]),
                            '%.4f' % float(r["firstAxisPos"]),
                            '%.4f' % float(r["firstAxisVelocity"]),
                            '%.4f' % float(r["secondAxisPos"]),
                            '%.4f' % float(r["secondAxisVelocity"])]
                    f_csv.writerow(line)
    
    def ztcallback(self, status):
        if self.cond.acquire():
            status["STAMP"] = str(time.time())
            print(status)
            self.que.put(status)
            self.cond.notify_all()
            self.cond.release()

    def ztfinishcb(self):
        self.issave = False
        msgBox = QMessageBox()
        msgBox.setWindowTitle("执行结束")
        msgBox.setText("转台运动结束，结果保存在history文件夹下")
        msgBox.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    # window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
