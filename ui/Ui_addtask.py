# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dev/zntk/ZNTKGUI/ui/addtask.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1014, 91)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../res/旋转.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_item = QtWidgets.QHBoxLayout()
        self.horizontalLayout_item.setObjectName("horizontalLayout_item")
        self.comboBox = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_item.addWidget(self.comboBox)
        self.label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout_item.addWidget(self.label)
        self.comboBox_2 = QtWidgets.QComboBox(Dialog)
        self.comboBox_2.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.horizontalLayout_item.addWidget(self.comboBox_2)
        self.label_2 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_item.addWidget(self.label_2)
        self.doubleSpinBox2 = QtWidgets.QDoubleSpinBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox2.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox2.setSizePolicy(sizePolicy)
        self.doubleSpinBox2.setMinimum(-360.0)
        self.doubleSpinBox2.setMaximum(360.0)
        self.doubleSpinBox2.setObjectName("doubleSpinBox2")
        self.horizontalLayout_item.addWidget(self.doubleSpinBox2)
        self.label_3 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_item.addWidget(self.label_3)
        self.doubleSpinBox1 = QtWidgets.QDoubleSpinBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox1.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox1.setSizePolicy(sizePolicy)
        self.doubleSpinBox1.setMinimum(-360.0)
        self.doubleSpinBox1.setMaximum(360.0)
        self.doubleSpinBox1.setObjectName("doubleSpinBox1")
        self.horizontalLayout_item.addWidget(self.doubleSpinBox1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_item.addWidget(self.label_4)
        self.doubleSpinBox3 = QtWidgets.QDoubleSpinBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox3.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox3.setSizePolicy(sizePolicy)
        self.doubleSpinBox3.setMinimum(-360.0)
        self.doubleSpinBox3.setMaximum(360.0)
        self.doubleSpinBox3.setObjectName("doubleSpinBox3")
        self.horizontalLayout_item.addWidget(self.doubleSpinBox3)
        self.label_5 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_item.addWidget(self.label_5)
        self.doubleSpinBox4 = QtWidgets.QDoubleSpinBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox4.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox4.setSizePolicy(sizePolicy)
        self.doubleSpinBox4.setMinimum(-360.0)
        self.doubleSpinBox4.setMaximum(360.0)
        self.doubleSpinBox4.setObjectName("doubleSpinBox4")
        self.horizontalLayout_item.addWidget(self.doubleSpinBox4)
        self.verticalLayout.addLayout(self.horizontalLayout_item)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "任务详情"))
        # self.comboBox.setItemText(0, _translate("Dialog", "开机一条龙(上电->闭合->归零->延时100s)"))
        # self.comboBox.setItemText(1, _translate("Dialog", "关机一条龙(停止->闲置->下电)"))
        # self.comboBox.setItemText(2, _translate("Dialog", "位置设置一条龙(位置方式设置->运行->延时)"))
        # self.comboBox.setItemText(3, _translate("Dialog", "速率设置一条龙(速率方式设置->运行->延时)"))
        # self.comboBox.setItemText(4, _translate("Dialog", "摇摆设置一条龙(摇摆方式设置->运行->延时)"))
        # self.comboBox.setItemText(5, _translate("Dialog", "上电"))
        # self.comboBox.setItemText(6, _translate("Dialog", "下电"))
        # self.comboBox.setItemText(7, _translate("Dialog", "闭合"))
        # self.comboBox.setItemText(8, _translate("Dialog", "闲置"))
        # self.comboBox.setItemText(9, _translate("Dialog", "运行"))
        # self.comboBox.setItemText(10, _translate("Dialog", "停止"))
        # self.comboBox.setItemText(11, _translate("Dialog", "位置方式设置"))
        # self.comboBox.setItemText(12, _translate("Dialog", "速率方式设置"))
        # self.comboBox.setItemText(13, _translate("Dialog", "摇摆方式设置"))
        # self.comboBox.setItemText(14, _translate("Dialog", "归零"))
        # self.comboBox.setItemText(15, _translate("Dialog", "停止归零"))
        # self.comboBox.setItemText(16, _translate("Dialog", "延时"))
        # self.comboBox.setItemText(17, _translate("Dialog", "循环开始"))
        # self.comboBox.setItemText(18, _translate("Dialog", "循环结束"))
        self.comboBox_2.setItemText(0, _translate("Dialog", "航向轴"))
        self.comboBox_2.setItemText(1, _translate("Dialog", "俯仰轴"))
        self.comboBox_2.setItemText(2, _translate("Dialog", "航向轴+俯仰轴"))
