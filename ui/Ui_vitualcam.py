# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\ZNTKGUI\ui\vitualcam.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1920, 1080)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dockWidget_3 = QtWidgets.QDockWidget(Dialog)
        self.dockWidget_3.setMinimumSize(QtCore.QSize(1000, 50))
        self.dockWidget_3.setFloating(True)
        self.dockWidget_3.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_3.setObjectName("dockWidget_3")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_plot = QtWidgets.QVBoxLayout()
        self.verticalLayout_plot.setObjectName("verticalLayout_plot")
        self.verticalLayout_3.addLayout(self.verticalLayout_plot)
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        self.horizontalLayout.addWidget(self.dockWidget_3)
        self.frame = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(6)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(900, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3d = QtWidgets.QVBoxLayout()
        self.verticalLayout_3d.setObjectName("verticalLayout_3d")
        self.dockWidget_2 = QtWidgets.QDockWidget(self.frame)
        self.dockWidget_2.setFloating(True)
        self.dockWidget_2.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_image = QtWidgets.QVBoxLayout()
        self.verticalLayout_image.setObjectName("verticalLayout_image")
        self.label_image = QtWidgets.QLabel(self.dockWidgetContents_2)
        self.label_image.setObjectName("label_image")
        self.verticalLayout_image.addWidget(self.label_image)
        self.horizontalLayout_2.addLayout(self.verticalLayout_image)
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        self.verticalLayout_3d.addWidget(self.dockWidget_2)
        self.verticalLayout_2.addLayout(self.verticalLayout_3d)
        self.horizontalLayout.addWidget(self.frame)
        self.dockWidget = QtWidgets.QDockWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.dockWidget.sizePolicy().hasHeightForWidth())
        self.dockWidget.setSizePolicy(sizePolicy)
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_table = QtWidgets.QVBoxLayout()
        self.verticalLayout_table.setObjectName("verticalLayout_table")
        self.verticalLayout_4.addLayout(self.verticalLayout_table)
        self.pushButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_4.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_4.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.verticalLayout_4)
        self.dockWidget.setWidget(self.dockWidgetContents)
        self.horizontalLayout.addWidget(self.dockWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.dockWidget_2.setWindowTitle(_translate("Dialog", "Camera"))
        self.label_image.setText(_translate("Dialog", "TextLabel"))
        self.pushButton.setText(_translate("Dialog", "添加"))
        self.pushButton_2.setText(_translate("Dialog", "插值"))
