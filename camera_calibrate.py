# -*- coding: utf-8 -*-
import cv2
import numpy as np
from scipy.spatial.transform import Rotation
import os
import sys
import copy
import yaml
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QListWidget, QWidget, QApplication, QListView, QHBoxLayout, QListWidgetItem, QDialog, QFileDialog
from ui.Ui_camera import Ui_Dialog
from plotCamera import PlotCamera
import piexif
import time

camera_type_list = ['omni-radtan', 'pinhole-equi', 'pinhole-radtan']
undistort_list = ['透视图', '圆柱图', '立体图', '世界地图']

class camCalibrateUtil(QThread):
    signal_image = pyqtSignal(object)
    signal_file = pyqtSignal(str)
    signal_pos = pyqtSignal(dict)
    def __init__(self, cap, checkboard_size, corner_num_x, corner_num_y):
        super(camCalibrateUtil, self).__init__()
        self.objpoints = []
        self.imgpoints = []
        self.cap = cap
        self.checkboard_size = checkboard_size
        self.corner_num_x = corner_num_x
        self.corner_num_y = corner_num_y
        self.prepare_to_shoot = False
        self.show_ori = False

        self.camera_type = 'omni-radtan'
        self.undistort_type = 0

        self.K = np.zeros((3, 3))
        self.xi = np.zeros((1, 1))
        self.D = np.zeros((4, 1))

    def stop(self):
        self.cap.release()

    def run(self):
        # 精准化角点迭代终止条件
        ctiteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, self.checkboard_size, 0.1)
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FILTER_QUADS + cv2.CALIB_CB_NORMALIZE_IMAGE
        flags_fisheye = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW
        flags_omni = cv2.omnidir.CALIB_USE_GUESS
        flags_omni_undistort = cv2.omnidir.RECTIFY_PERSPECTIVE

        # 世界坐标系中的棋盘格点
        obj_p = np.zeros((1, self.corner_num_x * self.corner_num_y, 3), dtype=np.float32)
        obj_p[0, :, :2] = np.mgrid[0:self.corner_num_x, 0:self.corner_num_y].T.reshape(-1, 2)

        count = 0
        while True:
            if self.undistort_type == 0:
                flags_omni_undistort = cv2.omnidir.RECTIFY_PERSPECTIVE
            elif self.undistort_type == 1:
                flags_omni_undistort = cv2.omnidir.RECTIFY_CYLINDRICAL
            elif self.undistort_type == 2:
                flags_omni_undistort = cv2.omnidir.RECTIFY_STEREOGRAPHIC
            elif self.undistort_type == 3:
                flags_omni_undistort = cv2.omnidir.RECTIFY_LONGLATI
            ret, frame = self.cap.read()
            if not ret:
                break
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            frame_down = np.copy(gray)
            gray = cv2.equalizeHist(gray)
            # 寻找棋盘格点
            ok, corners = cv2.findChessboardCorners(gray, (self.corner_num_x, self.corner_num_y), flags=flags)
            if ok:
                # 获取更精确的角点
                cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), ctiteria)
                # 显示在图像上
                cv2.drawChessboardCorners(frame, (self.corner_num_x, self.corner_num_y), corners, ok)
                if self.prepare_to_shoot:
                    self.objpoints.append(obj_p)
                    self.imgpoints.append(corners)
                    file_name = './images/{}.jpg'.format(str(time.strftime("%Y%m%d%H%M%S", time.localtime())))
                    cv2.imwrite(file_name, frame)
                    self.signal_file.emit(file_name)
                    tmp_objpoints = self.objpoints
                    tmp_imgpoints = self.imgpoints
                else:
                    tmp_objpoints = copy.copy(self.objpoints)
                    tmp_imgpoints = copy.copy(self.imgpoints)
                    tmp_objpoints.append(obj_p)
                    tmp_imgpoints.append(corners)
                if len(self.imgpoints) > 0:                  
                    # 
                    RR = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
                    TT = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
                    if self.camera_type == 'omni-radtan':
                        # omni-radtan相机标定
                        rms, K, xi, D, RR, TT, idx = cv2.omnidir.calibrate(
                            tmp_objpoints, 
                            tmp_imgpoints,
                            gray.shape[:2][::-1],
                            K=None, xi=None, D=None, flags=flags_omni,
                            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 200, 0.0001)
                        )
                    elif self.camera_type == 'pinhole-equi':
                        # 鱼眼相机标定
                        rms, K, D, _, _ = cv2.fisheye.calibrate(
                            self.objpoints, 
                            self.imgpoints,
                            gray.shape[:2][::-1],
                            K=None, D=None, rvecs=RR, tvecs=TT#, flags_fisheye, ctiteria
                        )
                        P = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, gray.shape[:2][::-1], None)
                    elif self.camera_type == 'pinhole-radtan':
                        # 针孔相机标定
                        rms, K, D, _, _ = cv2.calibrateCamera(
                            self.objpoints,
                            self.imgpoints,
                            gray.shape[:2][::-1],
                            cameraMatrix=None, distCoeffs=None, rvecs=RR, tvecs=TT
                        )
                    if self.prepare_to_shoot:
                        self.K = np.copy(K)
                        self.D = np.copy(D)
                        self.xi = np.copy(xi)
                        self.prepare_to_shoot = False
                    # print(self.K)
                    # print(self.D)
                    r = list(Rotation.from_rotvec(RR[-1].reshape((3,))).as_quat())
                    t = list(TT[-1].reshape((3,)) - TT[0].reshape((3,)))
                    pos = {
                        'q': r,
                        't': t
                    }
                    self.signal_pos.emit(pos)
            else:
                cv2.putText(gray, "FAIL TO FIND CORNERS", (int(0), int(frame_down.shape[0] / 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
            if not np.linalg.norm(self.K) == 0:
                try:
                    if self.camera_type == 'omni-radtan':
                        frame_undistort = cv2.omnidir.undistortImage(frame, self.K, self.D, self.xi, flags_omni_undistort)
                    elif self.camera_type == 'pinhole-equi':
                        frame_undistort = cv2.fisheye.undistortImage(frame, self.K, self.D)
                    elif self.camera_type == 'pinhole-radtan':
                        frame_undistort = cv2.undistort(frame, self.K, self.D)
                except ...:
                    print('expert errors when undistort')
                    frame_undistort = frame
                if self.camera_type == 'omni-radtan' and self.undistort_type > 0:
                    frame = frame_undistort
                else:
                    frame = cv2.addWeighted(frame_undistort, 0.5, frame, 0.5, 0)
            self.signal_image.emit(frame)


    def find_checkboard(self, frame, corner_num_x, corner_num_y):
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        ok, corners = cv2.findChessboardCorners(gray, (corner_num_x, corner_num_y))
        if ok:
            cv2.drawChessboardCorners(gray, (corner_num_x, corner_num_y), corners, ok)
            cv2.imshow('ok', gray)
            cv2.waitKey(0)


    def calibrate_online(self, cap, checkboard_size, corner_num_x, corner_num_y):
        '''
        cap:             要打开的相机
        checkboard_size: 棋盘格尺寸，单位mm
        corner_num_x:    横向棋盘格内角数量
        corner_num_y:    纵向棋盘格内角数量
        '''
        # 精准化角点迭代终止条件
        ctiteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, checkboard_size, 1e-6)
        flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
        flags_fisheye = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW

        # 世界坐标系中的棋盘格点
        obj_p = np.zeros((1, corner_num_x * corner_num_y, 3), dtype=np.float32)
        obj_p[0, :, :2] = np.mgrid[0:corner_num_x, 0:corner_num_y].T.reshape(-1, 2)

        count = 0
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            frame_down = np.copy(gray)
            gray = cv2.equalizeHist(gray)
            # 寻找棋盘格点
            ok, corners = cv2.findChessboardCorners(gray, (corner_num_x, corner_num_y))
            if ok:
                # 获取更精确的角点
                cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), ctiteria)
                # 显示在图像上
                cv2.drawChessboardCorners(gray, (corner_num_x, corner_num_y), corners, ok)
                key = cv2.waitKey(1) & 0xff
                if key == ord('c'):
                    self.objpoints.append(obj_p)
                    self.imgpoints.append(corners)
                    print('select {} pictures'.format(len(self.objpoints)))
                    # 鱼眼相机标定
                    K = np.zeros((3, 3))
                    D = np.zeros((4, 1))
                    RR = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
                    TT = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
                    rms, _, _, _, _ = cv2.fisheye.calibrate(
                        self.objpoints, 
                        self.imgpoints,
                        gray.shape[:2][::-1],
                        K, D, RR, TT#, flags_fisheye, ctiteria
                    )
                    # print('D={}'.format(D.tolist()))
                    P = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, gray.shape[:2][::-1], None)
                    print('D={}'.format(D.tolist()))
                    # 显示在图像上
                    # corners_undistort = cv2.fisheye.undistortPoints(corners, K, D)
                    # print("corners = {}".format(corners_undistort.tolist()))
                    # cv2.drawChessboardCorners(frame_down, (corner_num_x, corner_num_y), corners_undistort, ok)
                    # mapx, mapy = cv2.fisheye.initUndistortRectifyMap(K, D, None, P, gray.shape[:2][::-1], cv2.CV_32F)
                    # frame_down = cv2.remap(frame_down, mapx, mapy, interpolation=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
                    # print(frame_down.shape)
                    frame_down = cv2.fisheye.undistortImage(gray, K, D)
                    print(frame_down.shape)
                elif key == ord('s'):
                    cv2.imwrite('./history/{}.jpg'.format(count), frame)
                    count = count + 1
            else:
                cv2.putText(gray, "FAIL TO FIND CORNERS", (int(0), int(frame_down.shape[0] / 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
            show_img = cv2.vconcat([gray, frame_down])
            cv2.imshow("CAMERA CALIBRATE", show_img)
            key = cv2.waitKey(1) & 0xff
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('./history/{}.jpg'.format(count), frame)
                count = count + 1

class ImageListWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageListWidget, self).__init__(parent)
        self.resize(110, 768)
        self.setupUi()
    
    def setupUi(self):
        self.iconlist = QListWidget()
        self.iconlist.setViewMode(QListView.IconMode)
        self.iconlist.setSpacing(10)
        self.iconlist.setIconSize(QSize(200, 200))
        self.iconlist.setMovement(False)
        self.iconlist.setResizeMode(QListView.Adjust)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.iconlist)

        self.setLayout(hlayout)

    def addItem(self, file_name):
        exif = piexif.load(file_name)
        thumbnail = exif.pop('thumbnail')
        if thumbnail is not None:
            pix = QPixmap()
            
            pix.loadFromData(thumbnail, "JPG")
        else:
            pix = QPixmap()
            pix.load(file_name)

        item = QListWidgetItem(QIcon(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)), os.path.split(file_name)[-1])
        self.iconlist.addItem(item)
        self.iconlist.scrollToBottom()

class camviewDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(camviewDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.iconlist = ImageListWidget()
        self.verticalLayout_imagelist.addWidget(self.iconlist)
        for camera_type in camera_type_list:
            self.comboBox.addItem(camera_type)
        for undistort_type in undistort_list:
            self.comboBox_2.addItem(undistort_type)
        self.camerapos = PlotCamera(self.verticalLayout_camerapos)

        self.camerapos.add_pose([0, 0, 0], [0.0, 0.0, 0.0, 1.0])

        self.read_config()
        self.cam = None
        self.pushButton.clicked.connect(self.reopen)
        self.pushButton_2.clicked.connect(self.save)
        self.comboBox.currentIndexChanged.connect(self.on_change_camera_type)
        self.comboBox_2.currentIndexChanged.connect(self.on_change_display_type)

        self.reopen()

    def save(self):
        directory = QFileDialog.getSaveFileName(self, "结果保存", "../cam.txt", "文本文件 (*.txt)")
        if len(directory[0]) == 0:
            return
        with open(directory[0], 'w') as f:
            s = 'l_parameters:\r\n'
            f.write(s)
            s = '   k1: {}\r\n'.format(self.cam.D[0][0])
            f.write(s)
            s = '   k2: {}\r\n'.format(self.cam.D[0][1])
            f.write(s)
            s = '   p1: {}\r\n'.format(self.cam.D[0][2])
            f.write(s)
            s = '   p2: {}\r\n'.format(self.cam.D[0][3])
            f.write(s)
            s = '   xi: {}\r\n'.format(self.cam.xi[0][0])
            f.write(s)
            s = '   fx: {}\r\n'.format(self.cam.K[0, 0])
            f.write(s)
            s = '   fy: {}\r\n'.format(self.cam.K[1, 1])
            f.write(s)
            s = '   cx: {}\r\n'.format(self.cam.K[0, 2])
            f.write(s)
            s = '   cy: {}\r\n'.format(self.cam.K[1, 2])
            f.write(s)
            f.close()
        

    def reopen(self):
        if self.cam is not None:
            self.cam.stop()
            self.cam.quit()
            self.cam.wait()
            self.cam = None
        
        self.iconlist.iconlist.clear()
        
        camera_type = self.comboBox.currentText()
        camera_expose = self.horizontalSlider.value()
        camera_id = self.spinBox_cameraid.value()
        chessboard_corner_x = self.spinBox_cornerx.value()
        chessboard_corner_y = self.spinBox_cornery.value()
        chessboard_size = self.spinBox_size.value()

        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, camera_expose)
        self.cam = camCalibrateUtil(self.cap, chessboard_size, chessboard_corner_x, chessboard_corner_y)
        self.cam.camera_type = camera_type
        self.cam.signal_file.connect(self.add_image)
        self.cam.signal_image.connect(self.show_image)
        self.cam.signal_pos.connect(self.change_pos)

        self.cam.start()

    def on_change_display_type(self):
        display_type = self.comboBox_2.currentIndex()
        self.cam.undistort_type = display_type

    def on_change_camera_type(self):
        camera_type = self.comboBox.currentText()
        self.cam.camera_type = camera_type

    def read_config(self):
        with open("./config/camera_calibrate.yml",  encoding='utf-8') as f:
            yaml_cfg = yaml.load(f, Loader=yaml.FullLoader)
            chessboard_corner_x = yaml_cfg.get("chessboard_corner_x", 9)
            chessboard_corner_y = yaml_cfg.get("chessboard_corner_y", 6)
            chessboard_size = yaml_cfg.get("chessboard_size", 30)
            camera_mode = yaml_cfg.get("camera_mode", 0)
            camera_expose = yaml_cfg.get("camera_expose", -4)
            camera_id = yaml_cfg.get("camera_id", 0)

            self.comboBox.setCurrentIndex(camera_mode)
            self.horizontalSlider.setValue(camera_expose)
            self.spinBox_cameraid.setValue(camera_id)
            self.spinBox_cornerx.setValue(chessboard_corner_x)
            self.spinBox_cornery.setValue(chessboard_corner_y)
            self.spinBox_size.setValue(chessboard_size)

    def keyPressEvent(self, event):
        # print(str(event.key()))
        if (event.key() == Qt.Key_S):
            self.cam.prepare_to_shoot = True
        elif (event.key() == Qt.Key_Escape):
            self.cam.stop()
        return super().keyPressEvent(event)

    def closeEvent(self, event):
        self.cam.stop()

    def change_pos(self, pos):
        self.camerapos.add_pose(pos['t'], pos['q'])

    def add_image(self, file_name):
        self.iconlist.addItem(file_name)

    def show_image(self, image):
        convertToQtFormat = QtGui.QImage(
                image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        p = convertToQtFormat.scaled(
            self.label.width(), self.label.height(), Qt.KeepAspectRatio)
        self.label.setPixmap(QPixmap.fromImage(p))
        # print(image.shape)

if __name__ == "__main__":

    # cal = camCalibrateUtil()
    # cap = cv2.VideoCapture(700)
    # # cap = cv2.VideoCapture('C:/Users/wang/Pictures/Camera Roll/WIN_20210913_14_00_42_Pro.mp4')
    # # cap.set(cv2.CAP_PROP_IRIS, 200)
    # cap.set(cv2.CAP_PROP_EXPOSURE, -4)
    # cal.calibrate_online(cap, 27, 9, 6)
    # frame = cv2.imread('./history/18.jpg')
    # cal.find_checkboard(frame, 9, 6)
    app = QApplication(sys.argv)
    mainwin = camviewDialog()
    mainwin.show()
    sys.exit(app.exec_())




