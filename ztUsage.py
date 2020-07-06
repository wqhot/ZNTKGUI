# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTabWidget, QMainWindow, QMessageBox, QTableWidgetItem, QAction, QDialog
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QProcess
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QIcon
from PyQt5.QtWidgets import QLabel, QWidget
from ui.Ui_zttask import Ui_dialog as Ui_Dialog_zt
from ui.Ui_addtask import Ui_Dialog as Ui_Dialog_add
import os
import sys
import time
import csv
import threading
import queue
from zt920et import ztScheduler as ztScheduler_zt920et
from zt920et import ztTaskType as ztTaskType_zt920et
from zt901et import ztScheduler as ztScheduler_zt901et
from zt901et import ztTaskType as ztTaskType_zt901et
import serial.tools.list_ports
from recvIMU import RecvIMU

class ztUsage(QDialog, Ui_Dialog_zt):
    finishSignal = pyqtSignal()
    progessSignal = pyqtSignal(int, int)
    
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
        self.radioButton_2.clicked.connect(self.clearLst)
        self.radioButton.clicked.connect(self.clearLst)
        self.pushButton_6.clicked.connect(self.startRun)
        self.listWidget.doubleClicked.connect(self.modifyBtn)
        self.issave = False
        self.cond = threading.Condition()
        self.que = queue.Queue(1024)
        self.port_list = list(serial.tools.list_ports.comports())
        for port in self.port_list:
            self.comboBox.addItem(port.device)
            self.comboBox_2.addItem(port.device)
        if len(self.port_list) > 0:
            self.pushButton_6.setEnabled(True)
    
    def clearLst(self):
        self.lst.clear()
        self.listWidget.clear()

    def save(self):
        headers = ['stamp', 'firstAxisPos', 'firstAxisVelocity', 'secondAxisPos', 'secondAxisVelocity']
        csv_name = r'./history/' + \
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
                            str(float(r["firstAxisPos"])),
                            str(float(r["firstAxisVelocity"])),
                            str(float(r["secondAxisPos"])),
                            str(float(r["secondAxisVelocity"]))]
                    f_csv.writerow(line)

    def ztcallback(self, status):
        if self.cond.acquire():
            status["STAMP"] = str(time.time())
            print(status)
            self.que.put(status)
            self.cond.notify_all()
            self.cond.release()

    def finishCallback_mainThread(self):
        self.progressBar.setValue(100)
        self.progressBar.setEnabled(False)
        self.comboBox.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        self.radioButton.setEnabled(True)
        self.radioButton_2.setEnabled(True)
        self.listWidget.setEnabled(True)
        self.comboBox_2.setEnabled(True)
        msgBox = QMessageBox.information(self, "执行结束", "转台运动结束，结果保存在history文件夹下")

    def finishCallback(self):
        self.issave = False
        self.recv.isRecv = False
        self.finishSignal.emit()
        print("执行结束")       

    def progressCallback_mainThread(self, progress, fatherID):
        self.progressBar.setValue(progress)
        if fatherID > -1:
            self.listWidget.setCurrentRow(fatherID)
    
    def progressCallback(self, progress, fatherID):
        self.progessSignal.emit(int(progress * 100), fatherID)

    def startRun(self): 
        if self.comboBox.currentIndex() > 0:
            port = self.port_list[self.comboBox.currentIndex() - 1]
        else:
            port = None
        if self.comboBox_2.currentIndex() > 0:
            port_imu = self.port_list[self.comboBox_2.currentIndex() - 1]
        else:
            port_imu = None
        if self.comboBox_2.currentIndex() == self.comboBox.currentIndex() and port is not None:
            msgBox = QMessageBox.warning(self, "串口选择错误", "不能选择同样的串口")
            return
        if self.radioButton_2.isChecked():
            ss = ztScheduler_zt920et(
                readCallback=self.ztcallback, finishCallback=self.finishCallback, port=port)
        else:
            ss = ztScheduler_zt901et(
                readCallback=self.ztcallback, finishCallback=self.finishCallback, port=port)
        self.finishSignal.connect(self.finishCallback_mainThread)
        self.progessSignal.connect(self.progressCallback_mainThread)
        ss.setProgressCallback(self.progressCallback)
        taskLst = ss.createTasks(self.lst)
        if ss.zt902e1.connected:
            for t in taskLst:
                ss.addTask(t)
            self.progressBar.setEnabled(True)
            self.comboBox.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)
            self.listWidget.setEnabled(False)
            self.comboBox_2.setEnabled(False)
            self.issave = True
            self.recv = RecvIMU(port=port_imu)
            self.save_th = threading.Thread(target=self.save, daemon=True)
            self.save_th.start()
            ss.run(500)
        else:
            if port is None:
                self.progressBar.setEnabled(True)
                self.comboBox.setEnabled(False)
                self.pushButton_6.setEnabled(False)
                self.radioButton.setEnabled(False)
                self.radioButton_2.setEnabled(False)
                self.recv = RecvIMU(port=port_imu)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("通信失败")
                msgBox.setText("与转台间通信失败，请检查线缆是否连接正常")
                msgBox.exec()

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
        if self.radioButton_2.isChecked():
            opt1_s = ztTaskType_zt920et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt920et.type[task["id"]]["opt1"] else ""
            opt2_s = ztTaskType_zt920et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt920et.type[task["id"]]["opt2"] else ""
            opt3_s = ztTaskType_zt920et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt920et.type[task["id"]]["opt3"] else ""
            opt4_s = ztTaskType_zt920et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt920et.type[task["id"]]["opt4"] else ""
        else:
            opt1_s = ztTaskType_zt901et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt901et.type[task["id"]]["opt1"] else ""
            opt2_s = ztTaskType_zt901et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt901et.type[task["id"]]["opt2"] else ""
            opt3_s = ztTaskType_zt901et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt901et.type[task["id"]]["opt3"] else ""
            opt4_s = ztTaskType_zt901et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt901et.type[task["id"]]["opt4"] else ""
        s = "模式: " + str(task["text"]) + \
            "\t轴: " + str(task["axis"]) + \
            "\t" + opt1_s + "\t" + opt2_s + "\t" + opt3_s + "\t" + opt4_s
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
        self.addDialog.comboBox.clear()
        if self.radioButton_2.isChecked():
            for t in ztTaskType_zt920et.type:
                self.addDialog.comboBox.addItem(t["name"])
        else:
            for t in ztTaskType_zt901et.type:
                self.addDialog.comboBox.addItem(t["name"])
        self.addDialog.label.setText("选择设置的轴")
        self.select(task["id"])
        self.addDialog.comboBox.setCurrentIndex(task["id"])
        self.addDialog.comboBox_2.setCurrentIndex(task["axis"] - 1)
        self.addDialog.doubleSpinBox2.setValue(task["opt1"])
        self.addDialog.doubleSpinBox1.setValue(task["opt2"])
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
            task["opt1"] = self.addDialog.doubleSpinBox2.value()
            task["opt2"] = self.addDialog.doubleSpinBox1.value()
            task["opt3"] = self.addDialog.doubleSpinBox3.value()
            task["opt4"] = self.addDialog.doubleSpinBox4.value()
            if self.radioButton_2.isChecked():
                opt1_s = ztTaskType_zt920et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt920et.type[task["id"]]["opt1"] else ""
                opt2_s = ztTaskType_zt920et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt920et.type[task["id"]]["opt2"] else ""
                opt3_s = ztTaskType_zt920et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt920et.type[task["id"]]["opt3"] else ""
                opt4_s = ztTaskType_zt920et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt920et.type[task["id"]]["opt4"] else ""
            else:
                opt1_s = ztTaskType_zt901et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt901et.type[task["id"]]["opt1"] else ""
                opt2_s = ztTaskType_zt901et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt901et.type[task["id"]]["opt2"] else ""
                opt3_s = ztTaskType_zt901et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt901et.type[task["id"]]["opt3"] else ""
                opt4_s = ztTaskType_zt901et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt901et.type[task["id"]]["opt4"] else ""    
            s = "模式: " + str(task["text"]) + \
                "\t轴: " + str(task["axis"]) + \
                "\t" + opt1_s + "\t" + opt2_s + "\t" + opt3_s + "\t" + opt4_s
            self.lst[row] = task
            item = self.listWidget.takeItem(row)
            item.setText(s)
            self.listWidget.insertItem(row, item)
            self.listWidget.setCurrentRow(row)

    def addBtn(self):
        dialog = QDialog()
        self.addDialog = Ui_Dialog_add()
        self.addDialog.setupUi(dialog)
        self.addDialog.comboBox.clear()
        if self.radioButton_2.isChecked():
            for t in ztTaskType_zt920et.type:
                self.addDialog.comboBox.addItem(t["name"])
        else:
            for t in ztTaskType_zt901et.type:
                self.addDialog.comboBox.addItem(t["name"])
        self.addDialog.label.setText("选择设置的轴")
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
            task["opt1"] = self.addDialog.doubleSpinBox2.value()
            task["opt2"] = self.addDialog.doubleSpinBox1.value()
            task["opt3"] = self.addDialog.doubleSpinBox3.value()
            task["opt4"] = self.addDialog.doubleSpinBox4.value()
            if self.radioButton_2.isChecked():
                opt1_s = ztTaskType_zt920et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt920et.type[task["id"]]["opt1"] else ""
                opt2_s = ztTaskType_zt920et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt920et.type[task["id"]]["opt2"] else ""
                opt3_s = ztTaskType_zt920et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt920et.type[task["id"]]["opt3"] else ""
                opt4_s = ztTaskType_zt920et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt920et.type[task["id"]]["opt4"] else ""
            else:
                opt1_s = ztTaskType_zt901et.type[task["id"]]["opt1name"] + ": " + str(task["opt1"]) if ztTaskType_zt901et.type[task["id"]]["opt1"] else ""
                opt2_s = ztTaskType_zt901et.type[task["id"]]["opt2name"] + ": " + str(task["opt2"]) if ztTaskType_zt901et.type[task["id"]]["opt2"] else ""
                opt3_s = ztTaskType_zt901et.type[task["id"]]["opt3name"] + ": " + str(task["opt3"]) if ztTaskType_zt901et.type[task["id"]]["opt3"] else ""
                opt4_s = ztTaskType_zt901et.type[task["id"]]["opt4name"] + ": " + str(task["opt4"]) if ztTaskType_zt901et.type[task["id"]]["opt4"] else ""    
            s = "模式: " + str(task["text"]) + \
                "\t轴: " + str(task["axis"]) + \
                "\t" + opt1_s + "\t" + opt2_s + "\t" + opt3_s + "\t" + opt4_s
            newrow = self.listWidget.currentRow() + 1
            self.lst.insert(newrow, task)
            self.listWidget.insertItem(newrow, s)
            self.listWidget.setCurrentRow(newrow)

    def select(self, index):
        if self.radioButton_2.isChecked():
            self.addDialog.comboBox_2.setEnabled(ztTaskType_zt920et.type[index]["axis"])
            self.addDialog.label_2.setText(ztTaskType_zt920et.type[index]["opt1name"])
            self.addDialog.label_3.setText(ztTaskType_zt920et.type[index]["opt2name"])
            self.addDialog.label_4.setText(ztTaskType_zt920et.type[index]["opt3name"])
            self.addDialog.label_5.setText(ztTaskType_zt920et.type[index]["opt4name"])
            self.addDialog.doubleSpinBox2.setEnabled(ztTaskType_zt920et.type[index]["opt1"])
            self.addDialog.doubleSpinBox1.setEnabled(ztTaskType_zt920et.type[index]["opt2"])
            self.addDialog.doubleSpinBox3.setEnabled(ztTaskType_zt920et.type[index]["opt3"])
            self.addDialog.doubleSpinBox4.setEnabled(ztTaskType_zt920et.type[index]["opt4"])
        else:
            self.addDialog.comboBox_2.setEnabled(ztTaskType_zt901et.type[index]["axis"])
            self.addDialog.label_2.setText(ztTaskType_zt901et.type[index]["opt1name"])
            self.addDialog.label_3.setText(ztTaskType_zt901et.type[index]["opt2name"])
            self.addDialog.label_4.setText(ztTaskType_zt901et.type[index]["opt3name"])
            self.addDialog.label_5.setText(ztTaskType_zt901et.type[index]["opt4name"])
            self.addDialog.doubleSpinBox2.setEnabled(ztTaskType_zt901et.type[index]["opt1"])
            self.addDialog.doubleSpinBox1.setEnabled(ztTaskType_zt901et.type[index]["opt2"])
            self.addDialog.doubleSpinBox3.setEnabled(ztTaskType_zt901et.type[index]["opt3"])
            self.addDialog.doubleSpinBox4.setEnabled(ztTaskType_zt901et.type[index]["opt4"])

def cbTest(status):
    print(status)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    usbport = '/dev/ttyUSB1'
    if len(sys.argv) > 1:
        usbport = sys.argv[1]
    ex = ztUsage()
    ex.exec()
