# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/wq/catkin_ws/src/ZNTKGUI/bagset.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(262, 118)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 80, 191, 32))
        self.buttonBox.setStyleSheet("")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(80, 20, 171, 25))
        self.lineEdit.setStyleSheet("border:1px solid gray;\n"
"        border-radius:10px;\n"
"        padding:2px 4px;")
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 23, 54, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 54, 54, 17))
        self.label_2.setObjectName("label_2")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(Dialog)
        self.doubleSpinBox.setGeometry(QtCore.QRect(80, 50, 62, 26))
        self.doubleSpinBox.setStyleSheet("border:1px solid gray;\n"
"        border-radius:10px;\n"
"        padding:2px 4px;")
        self.doubleSpinBox.setMinimum(0.01)
        self.doubleSpinBox.setMaximum(1.0)
        self.doubleSpinBox.setSingleStep(0.02)
        self.doubleSpinBox.setProperty("value", 1.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "录制与回放"))
        self.lineEdit.setText(_translate("Dialog", "doubleIMUinit"))
        self.label.setText(_translate("Dialog", "包名"))
        self.label_2.setText(_translate("Dialog", "速率因子"))
