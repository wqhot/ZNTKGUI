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
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5


class analysisData():
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes = self.fig.add_subplot(111)
        self.data = {}
        self.ztData = {}
        self.analysisData = {}
        self.analysisZtData = {}
        self.analysisDataZeros = {}
        self.analysisZtDataZeros = {}
        self.fuData = []
        self.startStamp = 0
        cid = self.canvas.mpl_connect('button_press_event', self.onclick)

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

    def selectDataCols(self, cols):
        self.analysisData = {}
        self.analysisDataZeros = {}
        for col in cols:
            self.analysisData[col] = self.data[col]
            self.analysisDataZeros[col] = 0

    def selectZtDataCols(self, cols):
        self.analysisZtData = {}
        self.analysisZtDataZeros = {}
        for col in cols:
            self.analysisZtData[col] = self.ztData[col]
            self.analysisZtDataZeros[col] = 0

    def setFuData(self, labels):
        self.fuData = labels

    def analysis(self):
        # 对齐时间戳，取交集
        startStamp_data = self.data['stamp'][0]
        startStamp_ztData = self.ztData['stamp'][0]
        self.startStamp = startStamp_data if startStamp_data > startStamp_ztData else startStamp_ztData

        indexStart_data = np.where(self.data['stamp'] >= self.startStamp)
        indexStart_ztData = np.where(self.ztData['stamp'] >= self.startStamp)

        endStamp_data = self.data['stamp'][-1]
        endStamp_ztData = self.ztData['stamp'][-1]
        endStamp = endStamp_data if endStamp_data < endStamp_ztData else endStamp_ztData

        indexEnd_data = np.where(self.data['stamp'] <= endStamp)
        indexEnd_ztData = np.where(self.ztData['stamp'] <= endStamp)

        index_data = np.intersect1d(indexStart_data, indexEnd_data)
        index_ztData = np.intersect1d(indexStart_ztData, indexEnd_ztData)
        data_stamp = self.data['stamp'][index_data]
        ztData_stamp = self.ztData['stamp'][index_ztData]
        analysisData = {}
        analysisZtData = {}
        # 时间戳减去初始值
        data_stamp = data_stamp - \
            np.tile(self.startStamp, (len(index_data),))
        ztData_stamp = ztData_stamp - \
            np.tile(self.startStamp, (len(index_ztData),))

        for key in self.analysisData.keys():
            analysisData[key] = self.analysisData[key][index_data] - \
                np.tile(self.analysisDataZeros[key], self.analysisData[key][index_data].shape)
        # 对于zt数据需要插值
        for key in self.analysisZtData.keys():
            temp = self.analysisZtData[key][index_ztData] - \
                np.tile(self.analysisZtDataZeros[key], self.analysisZtData[key][index_ztData].shape)
            analysisZtData[key] = np.interp(data_stamp,
                                                 ztData_stamp,
                                                 temp)

        # 开始绘图
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        for key in analysisData.keys():
            if key in self.fuData:
                self.axes.plot(data_stamp,
                               -analysisData[key], label=key)
            else:
                self.axes.plot(data_stamp,
                               analysisData[key], label=key)
        for key in analysisZtData.keys():
            if key in self.fuData:
                self.axes.plot(data_stamp,
                               -analysisZtData[key], label=key)
            else:
                self.axes.plot(data_stamp,
                               analysisZtData[key], label=key)
        self.axes.legend()
        self.canvas.draw()
        self.canvas.flush_events()
        # self.axes.show()
        # plt.show()
        print(self.startStamp)

    def onclick(self, event):
        # print(event)
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
            self.analysis()
            print(self.analysisDataZeros)
            print(self.analysisZtDataZeros)


class analysisDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(analysisDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("分析")
        self.setMinimumSize(0, 0)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.datalabels = []
        self.ztdatalabels = []
        self.selectDatalabels = []
        self.selectZtDatalabels = []
        self.fuDatalabels = []
        # 第五步：定义MyFigure类的一个实例
        self.F = analysisData(width=3, height=2, dpi=100)
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

        self.pushButton_opendata.clicked.connect(self.openData)
        self.pushButton_openztdata.clicked.connect(self.openZtData)
        self.listWidget_1.doubleClicked.connect(self.addData)
        self.listWidget_2.doubleClicked.connect(self.delData)
        self.pushButton_2.clicked.connect(self.addData)
        self.pushButton.clicked.connect(self.delData)
        self.pushButton_3.clicked.connect(self.addFuData)
        # 补充：另创建一个实例绘图并显示
        # self.plotother()

    def refresh(self):
        self.F.selectDataCols(self.selectDatalabels)
        self.F.selectZtDataCols(self.selectZtDatalabels)
        self.F.setFuData(self.fuDatalabels)
        self.F.analysis()
        # self.figureLayout.removeWidget(self.toolbar)
        # self.figureLayout.removeWidget(self.F.canvas)
        # self.figureLayout.addWidget(self.toolbar)
        # self.figureLayout.addWidget(self.F.canvas)

    def addFuData(self):
        row = self.listWidget_1.currentRow()
        if row < 0:
            return
        label = self.listWidget_1.currentItem().text()
        item = self.listWidget_1.takeItem(row)
        self.fuDatalabels.append(label)
        if label in self.datalabels:
            self.selectDatalabels.append(label)
        else:
            self.selectZtDatalabels.append(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
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
        else:
            self.selectZtDatalabels.append(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
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
        else:
            self.selectZtDatalabels.remove(label)
        labels = []
        labels.extend(self.selectDatalabels)
        labels.extend(self.selectZtDatalabels)
        self.listWidget_2.clear()
        for item in labels:
            self.listWidget_2.addItem(item)
        self.listWidget_1.addItem(label)
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
        self.listWidget_1.clear()
        for item in labels:
            self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

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
        self.listWidget_1.clear()
        for item in labels:
            self.listWidget_1.addItem(item)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))


# test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = analysisDialog()
    main.show()
    # app.installEventFilter(main)
    sys.exit(app.exec_())
