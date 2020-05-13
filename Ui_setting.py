# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/wq/catkin_ws/src/ZNTKGUI/setting.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(312, 210)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(0, 170, 301, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(110, 20, 181, 25))
        self.lineEdit.setStyleSheet("border:1px solid gray;\n"
"        border-radius:10px;\n"
"        padding:2px 4px;")
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 20, 54, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(40, 60, 54, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(40, 107, 61, 17))
        self.label_3.setObjectName("label_3")
        self.lineEdit_3 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_3.setGeometry(QtCore.QRect(110, 100, 181, 25))
        self.lineEdit_3.setStyleSheet("border:1px solid gray;\n"
"        border-radius:10px;\n"
"        padding:2px 4px;")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(40, 150, 61, 17))
        self.label_4.setObjectName("label_4")
        self.lineEdit_4 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_4.setGeometry(QtCore.QRect(110, 140, 181, 25))
        self.lineEdit_4.setStyleSheet("border:1px solid gray;\n"
"        border-radius:10px;\n"
"        padding:2px 4px;")
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.spinBox = QtWidgets.QSpinBox(Dialog)
        self.spinBox.setGeometry(QtCore.QRect(110, 60, 51, 26))
        self.spinBox.setStyleSheet("border:1px solid gray;\n"
" border-radius:10px;\n"
"       padding:2px 4px;")
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(65535)
        self.spinBox.setProperty("value", 22)
        self.spinBox.setObjectName("spinBox")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "设置"))
        self.lineEdit.setText(_translate("Dialog", "10.42.0.1"))
        self.label.setText(_translate("Dialog", "IP"))
        self.label_2.setText(_translate("Dialog", "Port"))
        self.label_3.setText(_translate("Dialog", "username"))
        self.lineEdit_3.setText(_translate("Dialog", "shipei"))
        self.label_4.setText(_translate("Dialog", "password"))
        self.lineEdit_4.setText(_translate("Dialog", "shipei"))
