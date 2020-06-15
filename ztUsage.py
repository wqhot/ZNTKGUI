# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTabWidget, QMainWindow, QMessageBox, QTableWidgetItem, QAction, QDialog
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QProcess
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QIcon
from PyQt5.QtWidgets import QLabel, QWidget
from ui.Ui_zttask import Ui_dialog as Ui_Dialog_zt
from ui.Ui_addtask import Ui_Dialog as Ui_Dialog_add
import sys
from zt902e1 import ztScheduler, ztTask
# dialog = QDialog()
# setDialog = Ui_Dialog_zt()
# setDialog.setupUi(dialog)
# if dialog.exec():
#     pass


class ztUsage(QDialog, Ui_Dialog_zt):
    def __init__(self):
        super().__init__()
        self.lst = []
        self.setupUi(self)
        self.pushButton.setStyleSheet("QPushButton{border-image: url(res/添加.png)}"
                                      "QPushButton:hover{border-image: url(res/添加1.png)}"
                                      "QPushButton:pressed{border-image: url(res/添加.png)}")
        self.pushButton_2.setStyleSheet("QPushButton{border-image: url(res/向上.png)}"
                                      "QPushButton:hover{border-image: url(res/向上1.png)}"
                                      "QPushButton:pressed{border-image: url(res/向上.png)}")
        self.pushButton_3.setStyleSheet("QPushButton{border-image: url(res/向下.png)}"
                                      "QPushButton:hover{border-image: url(res/向下1.png)}"
                                      "QPushButton:pressed{border-image: url(res/向下.png)}")
        self.pushButton_4.setStyleSheet("QPushButton{border-image: url(res/关闭.png)}"
                                      "QPushButton:hover{border-image: url(res/关闭1.png)}"
                                      "QPushButton:pressed{border-image: url(res/关闭.png)}")
        self.pushButton_5.setStyleSheet("QPushButton{border-image: url(res/复制.png)}"
                                      "QPushButton:hover{border-image: url(res/复制1.png)}"
                                      "QPushButton:pressed{border-image: url(res/复制.png)}")
        self.pushButton.clicked.connect(self.addBtn)
        self.pushButton_2.clicked.connect(self.moveUpBtn)
        self.pushButton_3.clicked.connect(self.moveDownBtn)
        self.pushButton_4.clicked.connect(self.delBtn)
        self.pushButton_5.clicked.connect(self.copyBtn)
        self.pushButton_5.setShortcut('Ctrl+C')
        self.listWidget.doubleClicked.connect(self.modifyBtn)

    def moveUpBtn(self):
        newrow = self.listWidget.currentRow() - 1
        currow = self.listWidget.currentRow()
        if newrow < 0:
            return
        self.lst[newrow], self.lst[currow] = self.lst[currow], self.lst[newrow]
        nrow = self.listWidget.takeItem(self.listWidget.currentRow() - 1)
        crow = self.listWidget.takeItem(self.listWidget.currentRow())
        self.listWidget.insertItem(newrow, crow)
        self.listWidget.insertItem(currow, nrow)
        self.listWidget.setCurrentRow(newrow)

    def moveDownBtn(self):
        newrow = self.listWidget.currentRow() + 1
        currow = self.listWidget.currentRow()
        if newrow > len(self.lst) - 1:
            return
        self.lst[newrow], self.lst[currow] = self.lst[currow], self.lst[newrow]
        nrow = self.listWidget.takeItem(self.listWidget.currentRow() + 1)
        crow = self.listWidget.takeItem(self.listWidget.currentRow())
        self.listWidget.insertItem(currow, nrow)
        self.listWidget.insertItem(newrow, crow)
        self.listWidget.setCurrentRow(newrow)

    def delBtn(self):
        currow = self.listWidget.currentRow()
        if currow >= 0:
            self.lst.remove(self.lst[currow])
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.listWidget.setCurrentRow(currow - 1)

    def copyBtn(self):
        row = self.listWidget.currentRow()
        if row < 0:
            return
        task = self.lst[row]
        s = "模式: %s, 轴: %d, 选项1: %f, 选项2: %f, 选项3: %f, 选项4: %f" % \
            (task["text"], task["axis"], task["opt1"],
            task["opt2"], task["opt3"], task["opt4"])
        newrow = self.listWidget.currentRow() + 1
        self.lst.insert(newrow, task)
        self.listWidget.insertItem(newrow, s)
        self.listWidget.setCurrentRow(newrow)

    def modifyBtn(self):
        row = self.listWidget.currentRow()
        task = self.lst[row]
        dialog = QDialog()
        self.addDialog = Ui_Dialog_add()
        self.addDialog.setupUi(dialog)
        self.addDialog.comboBox.setCurrentIndex(task["id"])
        self.addDialog.comboBox_2.setCurrentIndex(task["axis"] - 1)
        self.addDialog.doubleSpinBox1.setValue(task["opt1"])
        self.addDialog.doubleSpinBox2.setValue(task["opt2"])
        self.addDialog.doubleSpinBox3.setValue(task["opt3"])
        self.addDialog.doubleSpinBox4.setValue(task["opt4"])
        self.addDialog.comboBox.currentIndexChanged.connect(self.select)
        # addDialog.comboBox.activated.connect(self.select, addDialog)
        if dialog.exec():
            # 只能设置单一的轴
            if self.addDialog.comboBox.currentIndex() in [2, 3, 4, 11, 12, 13, 14, 15] and \
                    self.addDialog.comboBox_2.currentIndex() == 2:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("轴设置错误")
                msgBox.setText("该模式下只能设置一个轴")
                msgBox.exec()
                return
            task = {}
            task["id"] = self.addDialog.comboBox.currentIndex()
            task["text"] = self.addDialog.comboBox.currentText()
            task["axis"] = self.addDialog.comboBox_2.currentIndex() + 1
            task["opt1"] = self.addDialog.doubleSpinBox1.value()
            task["opt2"] = self.addDialog.doubleSpinBox2.value()
            task["opt3"] = self.addDialog.doubleSpinBox3.value()
            task["opt4"] = self.addDialog.doubleSpinBox4.value()
            s = "模式: %s, 轴: %d, 选项1: %f, 选项2: %f, 选项3: %f, 选项4: %f" % \
                (task["text"], task["axis"], task["opt1"],
                 task["opt2"], task["opt3"], task["opt4"])
            self.lst[row] = task
            item = self.listWidget.takeItem(row)
            item.setText(s)
            self.listWidget.insertItem(row, item)
            self.listWidget.setCurrentRow(row)

    def addBtn(self):
        dialog = QDialog()
        self.addDialog = Ui_Dialog_add()
        self.addDialog.setupUi(dialog)
        self.addDialog.comboBox.currentIndexChanged.connect(self.select)
        # addDialog.comboBox.activated.connect(self.select, addDialog)
        if dialog.exec():
            # 只能设置单一的轴
            if self.addDialog.comboBox.currentIndex() in [2, 3, 4, 11, 12, 13, 14, 15] and \
                    self.addDialog.comboBox_2.currentIndex() == 2:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("轴设置错误")
                msgBox.setText("该模式下只能设置一个轴")
                msgBox.exec()
                return
            task = {}
            task["id"] = self.addDialog.comboBox.currentIndex()
            task["text"] = self.addDialog.comboBox.currentText()
            task["axis"] = self.addDialog.comboBox_2.currentIndex() + 1
            task["opt1"] = self.addDialog.doubleSpinBox1.value()
            task["opt2"] = self.addDialog.doubleSpinBox2.value()
            task["opt3"] = self.addDialog.doubleSpinBox3.value()
            task["opt4"] = self.addDialog.doubleSpinBox4.value()
            s = "模式: %s, 轴: %d, 选项1: %f, 选项2: %f, 选项3: %f, 选项4: %f" % \
                (task["text"], task["axis"], task["opt1"],
                 task["opt2"], task["opt3"], task["opt4"])
            newrow = self.listWidget.currentRow() + 1
            self.lst.insert(newrow, task)
            self.listWidget.insertItem(newrow, s)
            self.listWidget.setCurrentRow(newrow)

    def select(self, index):
        self.addDialog.label.setText("选择设置的轴")
        self.addDialog.label_2.setText("无效")
        self.addDialog.label_3.setText("无效")
        self.addDialog.label_4.setText("无效")
        self.addDialog.label_5.setText("无效")
        # 位置设置一条龙
        if index == 2:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("目标角度")
            self.addDialog.label_3.setText("目标速度")
            self.addDialog.label_4.setText("目标加速度")
            self.addDialog.label_5.setText("保持时间")
        # 速率设置一条龙
        elif index == 3:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("目标速度")
            self.addDialog.label_3.setText("目标加速度")
            self.addDialog.label_4.setText("保持时间")
        # 摇摆设置一条龙
        elif index == 4:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("幅度")
            self.addDialog.label_3.setText("频率")
            self.addDialog.label_4.setText("时长")
        # 位置方式设置
        elif index == 11:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("目标角度")
            self.addDialog.label_3.setText("目标速度")
            self.addDialog.label_4.setText("目标加速度")
        # 速率设置
        elif index == 12:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("目标速度")
            self.addDialog.label_3.setText("目标加速度")
        # 摇摆设置
        elif index == 13:
            self.addDialog.label.setText("选择设置的轴")
            self.addDialog.label_2.setText("幅度")
            self.addDialog.label_3.setText("频率")
            self.addDialog.label_4.setText("时长")
        # 空闲
        elif index == 16:
            self.addDialog.label.setText("无效")
            self.addDialog.label_2.setText("保持时间")

    def createTasks(self, oriTasks):
        taskLst = []
        runtype1 = 5
        runtype2 = 5
        for t in oriTasks:
            # 开机一条龙
            if t["id"] == 0:
                task = ztTask(type=1, axis=t["axis"])
                taskLst.append(task)
                task = ztTask(type=3, axis=t["axis"])
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    task = ztTask(type=0x0b, axis=1)
                    taskLst.append(task)
                    task = ztTask(type=0xd, delay=100)
                    taskLst.append(task)
                if t["axis"] & 2 != 0:
                    task = ztTask(type=0x0b, axis=2)
                    taskLst.append(task)
                    task = ztTask(type=0xd, delay=100)
                    taskLst.append(task)
            # 关机一条龙
            if t["id"] == 1:
                task = ztTask(type=6, axis=t["axis"])
                taskLst.append(task)
                task = ztTask(type=4, axis=t["axis"])
                taskLst.append(task)
                task = ztTask(type=2, axis=t["axis"])
                taskLst.append(task)

            # 位置设置一条龙
            if t["id"] == 2:
                task = ztTask(
                    type=7, axis=t["axis"], pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"])
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=5, runType_2=5)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"])
                taskLst.append(task)

            # 速率设置一条龙
            if t["id"] == 3:
                task = ztTask(type=8, axis=t["axis"],
                              vel_v=t["opt1"], vel_a=t["opt2"])
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=6, runType_2=6)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"])
                taskLst.append(task)

            # 摇摆设置一条龙
            if t["id"] == 4:
                task = ztTask(
                    type=9, axis=t["axis"], swing_range=t["opt1"], swing_freq=t["opt2"], swing_dur=t["opt3"])
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=7, runType_2=7)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt3"] + 1)
                taskLst.append(task)

            # 上电 下电 闭合 闲置 运行 停止
            if t["id"] in [5, 6, 7, 8, 9, 10]:
                task = ztTask(type=t["id"] - 4, axis=t["axis"],
                              runType_1=runtype1, runType_2=runtype2)
                taskLst.append(task)

            # 位置设置
            if t["id"] == 11:
                task = ztTask(
                    type=7, axis=t["axis"], pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"])
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 5
                if t["axis"] & 2 != 0:
                    runtype2 = 5
            # 速率设置
            if t["id"] == 12:
                task = ztTask(type=8, axis=t["axis"],
                              vel_v=t["opt1"], vel_a=t["opt2"])
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 6
                if t["axis"] & 2 != 0:
                    runtype2 = 6

            # 摇摆设置
            if t["id"] == 13:
                task = ztTask(
                    type=9, axis=t["axis"], swing_range=t["opt1"], swing_freq=t["opt2"], swing_dur=t["opt3"])
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 7
                if t["axis"] & 2 != 0:
                    runtype2 = 7

            # 归零 停止归零
            if t["id"] in [14, 15]:
                task = ztTask(type=t["id"] - 3, axis=t["axis"])
                taskLst.append(task)

            # 保持
            if t["id"] == 16:
                task = ztTask(type=0x0d, delay=t["opt1"])
                taskLst.append(task)
        return taskLst


def cbTest(status):
    print(status)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    usbport = '/dev/ttyUSB1'
    if len(sys.argv) > 1:
        usbport = sys.argv[1]
    ex = ztUsage()
    if ex.exec():
        print(ex.lst)
        taskLst = ex.createTasks(ex.lst)
        ss = ztScheduler(readCallback=cbTest, portname=usbport)
        if ss.zt902e1.connected:
            for t in taskLst:
                ss.addTask(t)
            ss.run(1)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("通信失败")
            msgBox.setText("与转台间通信失败，请检查线缆是否连接正常")
            msgBox.exec()
