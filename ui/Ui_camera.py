# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ZNTKGUI\ui\camera.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1252, 751)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/棋盘.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_9.addWidget(self.label_2)
        self.comboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_9.addWidget(self.comboBox)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_10.addWidget(self.label_8)
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_10.addWidget(self.comboBox_2)
        self.verticalLayout_5.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_3.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_8.addWidget(self.label_3)
        self.horizontalSlider = QtWidgets.QSlider(self.groupBox)
        self.horizontalSlider.setMinimum(-10)
        self.horizontalSlider.setMaximum(0)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.horizontalSlider.setTickInterval(1)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout_8.addWidget(self.horizontalSlider)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.spinBox_cornerx = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_cornerx.setObjectName("spinBox_cornerx")
        self.horizontalLayout_4.addWidget(self.spinBox_cornerx)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_7.addWidget(self.label_6)
        self.spinBox_cornery = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_cornery.setObjectName("spinBox_cornery")
        self.horizontalLayout_7.addWidget(self.spinBox_cornery)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.spinBox_size = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_size.setMaximum(99)
        self.spinBox_size.setObjectName("spinBox_size")
        self.horizontalLayout_6.addWidget(self.spinBox_size)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_8.addWidget(self.label_7)
        self.spinBox_cameraid = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_cameraid.setMaximum(9999)
        self.spinBox_cameraid.setObjectName("spinBox_cameraid")
        self.horizontalLayout_8.addWidget(self.spinBox_cameraid)
        self.horizontalLayout_3.addWidget(self.groupBox)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.pushButton_calonce = QtWidgets.QPushButton(Dialog)
        self.pushButton_calonce.setObjectName("pushButton_calonce")
        self.horizontalLayout_11.addWidget(self.pushButton_calonce)
        self.pushButton_project = QtWidgets.QPushButton(Dialog)
        self.pushButton_project.setObjectName("pushButton_project")
        self.horizontalLayout_11.addWidget(self.pushButton_project)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.label_9 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setMaximumSize(QtCore.QSize(410, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(0)
        self.frame.setObjectName("frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_imagelist = QtWidgets.QVBoxLayout()
        self.verticalLayout_imagelist.setSpacing(0)
        self.verticalLayout_imagelist.setObjectName("verticalLayout_imagelist")
        self.verticalLayout_3.addLayout(self.verticalLayout_imagelist)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_7.addWidget(self.label_10)
        self.doubleSpinBox_kfx = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_kfx.setMinimum(0.0)
        self.doubleSpinBox_kfx.setMaximum(999.99)
        self.doubleSpinBox_kfx.setObjectName("doubleSpinBox_kfx")
        self.verticalLayout_7.addWidget(self.doubleSpinBox_kfx)
        self.doubleSpinBox_kfy = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_kfy.setMinimum(0.0)
        self.doubleSpinBox_kfy.setMaximum(999.99)
        self.doubleSpinBox_kfy.setObjectName("doubleSpinBox_kfy")
        self.verticalLayout_7.addWidget(self.doubleSpinBox_kfy)
        self.doubleSpinBox_kcx = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_kcx.setMinimum(0.0)
        self.doubleSpinBox_kcx.setMaximum(999.99)
        self.doubleSpinBox_kcx.setObjectName("doubleSpinBox_kcx")
        self.verticalLayout_7.addWidget(self.doubleSpinBox_kcx)
        self.doubleSpinBox_kcy = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_kcy.setMinimum(0.0)
        self.doubleSpinBox_kcy.setMaximum(999.99)
        self.doubleSpinBox_kcy.setObjectName("doubleSpinBox_kcy")
        self.verticalLayout_7.addWidget(self.doubleSpinBox_kcy)
        self.horizontalLayout_13.addLayout(self.verticalLayout_7)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_11 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_8.addWidget(self.label_11)
        self.doubleSpinBox_dk1 = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_dk1.setMinimum(-99.0)
        self.doubleSpinBox_dk1.setObjectName("doubleSpinBox_dk1")
        self.verticalLayout_8.addWidget(self.doubleSpinBox_dk1)
        self.doubleSpinBox_dk2 = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_dk2.setMinimum(-99.0)
        self.doubleSpinBox_dk2.setObjectName("doubleSpinBox_dk2")
        self.verticalLayout_8.addWidget(self.doubleSpinBox_dk2)
        self.doubleSpinBox_dp1 = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_dp1.setMinimum(-99.0)
        self.doubleSpinBox_dp1.setObjectName("doubleSpinBox_dp1")
        self.verticalLayout_8.addWidget(self.doubleSpinBox_dp1)
        self.doubleSpinBox_dp2 = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_dp2.setMinimum(-99.0)
        self.doubleSpinBox_dp2.setObjectName("doubleSpinBox_dp2")
        self.verticalLayout_8.addWidget(self.doubleSpinBox_dp2)
        self.doubleSpinBox_xi = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_xi.setMinimum(-99.0)
        self.doubleSpinBox_xi.setObjectName("doubleSpinBox_xi")
        self.verticalLayout_8.addWidget(self.doubleSpinBox_xi)
        self.horizontalLayout_13.addLayout(self.verticalLayout_8)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_12 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_6.addWidget(self.label_12)
        self.doubleSpinBox_err = QtWidgets.QDoubleSpinBox(self.frame)
        self.doubleSpinBox_err.setObjectName("doubleSpinBox_err")
        self.verticalLayout_6.addWidget(self.doubleSpinBox_err)
        self.horizontalLayout_13.addLayout(self.verticalLayout_6)
        self.horizontalLayout_12.addLayout(self.horizontalLayout_13)
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setMinimumSize(QtCore.QSize(200, 200))
        self.frame_2.setMaximumSize(QtCore.QSize(200, 200))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_camerapos = QtWidgets.QVBoxLayout()
        self.verticalLayout_camerapos.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout_camerapos.setObjectName("verticalLayout_camerapos")
        self.horizontalLayout_2.addLayout(self.verticalLayout_camerapos)
        self.horizontalLayout_12.addWidget(self.frame_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_12)
        self.horizontalLayout.addWidget(self.frame)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox_2.setTitle(_translate("Dialog", "实时生效"))
        self.label_2.setText(_translate("Dialog", "相机模型"))
        self.label_8.setText(_translate("Dialog", "显示模式"))
        self.groupBox.setTitle(_translate("Dialog", "需要刷新才能生效"))
        self.label_3.setText(_translate("Dialog", "曝光时间"))
        self.label_5.setText(_translate("Dialog", "棋盘格横向交叉点"))
        self.label_6.setText(_translate("Dialog", "棋盘格横向交叉点"))
        self.label_4.setText(_translate("Dialog", "棋盘格宽度(mm)"))
        self.label_7.setText(_translate("Dialog", "相机设备号"))
        self.pushButton_2.setText(_translate("Dialog", "保存结果"))
        self.pushButton.setText(_translate("Dialog", "刷新"))
        self.pushButton_calonce.setText(_translate("Dialog", "畸变计算"))
        self.pushButton_project.setText(_translate("Dialog", "效果评价"))
        self.label_9.setText(_translate("Dialog", "图像大于10张后自行关闭实时畸变计算"))
        self.label.setText(_translate("Dialog", "图像"))
        self.label_10.setText(_translate("Dialog", "K"))
        self.label_11.setText(_translate("Dialog", "D"))
        self.label_12.setText(_translate("Dialog", "ERROR"))
        self.pushButton_3.setText(_translate("Dialog", "拍照(Ctrl+S)"))
        self.pushButton_3.setShortcut(_translate("Dialog", "Ctrl+S"))

