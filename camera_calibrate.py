# -*- coding: utf-8 -*-
from __future__ import print_function
import ctypes
from ctypes import *
import sys
from tabnanny import check

from attr import has
from nokov_camera import NOKOVCamera

# from Demo_opencv_byCallBack import HGDLCamera

# def is_admin():
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except:
#         return False
# if is_admin():
#     pass
# else:
#     if sys.version_info[0] == 3:
#         ctypes.windll.shell32.ShellExecuteW(
#             None, "runas", sys.executable, __file__, None, 1)
#     else:  # in python2.x
#         ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(
#             sys.executable), unicode(__file__), None, 1)
#     exit(0)

import cv2
import numpy as np
from scipy.spatial.transform import Rotation
import os
import sys
import copy
import yaml
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QListWidget, QDoubleSpinBox, QSpinBox, QWidget, QLabel, QApplication, QListView, QHBoxLayout, QVBoxLayout, QListWidgetItem, QDialog, QFileDialog, QTableWidget, QTableWidgetItem
from ui.Ui_camera import Ui_Dialog
from plotCamera import PlotCamera
# from Demo_opencv_byGetFrame import *
import piexif
import time
import datetime
import zipfile

camera_type_list = ['pinhole-radtan', 'omni-radtan', 'pinhole-equi']
undistort_list = ['透视图', '圆柱图', '立体图', '世界地图', '原图', '仅透视图 ']

def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath,'')

        for filename in filenames:
            zip.write(os.path.join(path,filename),os.path.join(fpath,filename))
    zip.close()

class camCalibrateUtil(QThread):
    signal_image = pyqtSignal(object)
    signal_file = pyqtSignal(str)
    signal_pos = pyqtSignal(dict)
    signal_para = pyqtSignal(dict)
    def __init__(self, cap, checkboard_size, corner_num_x, corner_num_y):
        super(camCalibrateUtil, self).__init__()
        self.objpoints = []
        self.imgpoints = []
        self.real_r = []
        self.real_t = []
        self.cap = cap
        self.checkboard_size = checkboard_size
        self.corner_num_x = corner_num_x
        self.corner_num_y = corner_num_y
        self.prepare_to_shoot = False
        self.show_ori = False
        self.cal_online = True
        self.raw_dict = './images/' + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
        if not os.path.exists(self.raw_dict):
            os.makedirs(self.raw_dict)
        self.img_shape = (int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print(self.img_shape)
        self.mask = None
        # 0 无 1 短边 2 长边
        self.mask_type = 0

        self.camera_type = 'pinhole-radtan'
        self.undistort_type = 0

        self.K = np.zeros((3, 3))
        self.xi = np.zeros((1, 1))
        self.D = np.zeros((4, 1))

    def __del__(self):
        zipDir(self.raw_dict, self.raw_dict + '.zip')

    def gen_mask(self):
        if self.mask_type == 0:
            self.mask = None
            return
        elif self.mask_type == 1:
            l = min(self.img_shape) / 2
        elif self.mask_type == 2:
            l = max(self.img_shape) / 2
        self.mask = np.zeros(shape=self.img_shape, dtype=np.uint8)
        c = (self.img_shape[0] / 2, self.img_shape[1] / 2)
        x_dist = np.matrix((np.arange(0, self.img_shape[1], 1, dtype=np.float64) - c[1]) ** 2)
        x_dist = np.repeat(x_dist, self.img_shape[0], axis=0)
        y_dist = np.matrix((np.arange(0, self.img_shape[0], 1, dtype=np.float64) - c[0]) ** 2).T
        y_dist = np.repeat(y_dist, self.img_shape[1], axis=1)
        dist = np.sqrt(x_dist + y_dist)
        self.mask[dist < l] = 1


    def stop(self):
        self.cap.release()

    def cal_once(self):
        flags_omni = cv2.omnidir.CALIB_USE_GUESS
        if len(self.imgpoints) > 0:
            RR = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
            TT = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
            self.real_r = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
            self.real_t = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(self.objpoints))]
            if self.camera_type == 'omni-radtan':
                # omni-radtan相机标定
                rms, self.K, self.xi, self.D, RR, TT, idx = cv2.omnidir.calibrate(
                    self.objpoints, 
                    self.imgpoints,
                    self.img_shape[:2][::-1],
                    K=None, xi=None, D=None, flags=flags_omni,
                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 200, 0.0001)
                )
            elif self.camera_type == 'pinhole-equi':
                # 鱼眼相机标定
                rms, self.K, self.D, RR, TT = cv2.fisheye.calibrate(
                    self.objpoints, 
                    self.imgpoints,
                    self.img_shape[:2][::-1],
                    K=None, D=None, rvecs=RR, tvecs=TT#, flags_fisheye, ctiteria
                )
                P = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(self.K, self.D, self.img_shape[:2][::-1], None)
            elif self.camera_type == 'pinhole-radtan':
                # 针孔相机标定
                rms, self.K, self.D, RR, TT = cv2.calibrateCamera(
                    self.objpoints, 
                    self.imgpoints,
                    self.img_shape[:2][::-1],
                    cameraMatrix=None, distCoeffs=None, rvecs=RR, tvecs=TT
                )
            sig_d = {"K":self.K, "D":self.D, "xi":self.xi}
            self.signal_para.emit(sig_d)
    
    def project(self, rot, trans):
        rvecs = rot.as_rotvec()
        tvecs = trans
        mean_error = 0
        for row, objpoint in enumerate(self.objpoints):
            if self.camera_type == 'omni-radtan':
                # omni-radtan相机反投影
                img_points, _ = cv2.omnidir.projectPoints(
                    objpoint, 
                    rvecs[row, :],
                    tvecs[row, :],
                    K=self.K, xi=self.xi[0][0], D=self.D
                )
            elif self.camera_type == 'pinhole-equi':
                # 鱼眼相机反投影
                img_points, _ = cv2.fisheye.projectPoints(
                    objpoint, 
                    rvecs[row, :],
                    tvecs[row, :],
                    K=self.K, D=self.D
                )
            elif self.camera_type == 'pinhole-radtan':
                # 针孔相机反投影
                img_points, _ = cv2.projectPoints(
                    objpoint, 
                    rvecs[row, :],
                    tvecs[row, :],
                    K=self.K, D=self.D
                )
            err = cv2.norm(self.imgpoints[row].reshape(img_points.shape), img_points, cv2.NORM_L2) / len(img_points)
            mean_error = mean_error + err
        mean_error = mean_error / len(self.objpoints)
        return mean_error

    def run(self):
        # 精准化角点迭代终止条件
        ctiteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, self.checkboard_size, 0.1)
        flags = cv2.CALIB_CB_FILTER_QUADS + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK 
        flags_fisheye = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW
        flags_omni = cv2.omnidir.CALIB_USE_GUESS
        flags_omni_undistort = cv2.omnidir.RECTIFY_PERSPECTIVE

        # 世界坐标系中的棋盘格点
        obj_p = np.zeros((1, self.corner_num_x * self.corner_num_y, 3), dtype=np.float32)
        obj_p[0, :, :2] = np.mgrid[0:self.corner_num_x, 0:self.corner_num_y].T.reshape(-1, 2)
        xi = np.zeros((1, 1))

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
            else:
                flags_omni_undistort = cv2.omnidir.RECTIFY_PERSPECTIVE
            start = time.perf_counter()  # 返回系统运行时间
            ret, frame = self.cap.read()
            if not ret:
                print("ret is false")
                break
            if self.mask is not None:
                temp = np.zeros(shape=frame.shape, dtype=frame.dtype)
                frame = cv2.bitwise_and(frame, frame, mask=self.mask)
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_down = np.copy(gray)
            # gray = cv2.equalizeHist(gray)
            self.img_shape = gray.shape
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
                    file_name_raw = self.raw_dict + '/{}.jpg'.format(str(time.strftime("%Y%m%d%H%M%S", time.localtime())))
                    cv2.imwrite(file_name, frame)
                    cv2.imwrite(file_name_raw, gray)
                    self.signal_file.emit(file_name)
                    tmp_objpoints = self.objpoints
                    tmp_imgpoints = self.imgpoints
                else:
                    tmp_objpoints = copy.copy(self.objpoints)
                    tmp_imgpoints = copy.copy(self.imgpoints)
                    tmp_objpoints.append(obj_p)
                    tmp_imgpoints.append(corners)
                if len(self.imgpoints) > 10:
                    self.cal_online = False
                if len(tmp_objpoints) > 0 and len(tmp_imgpoints) > 0 and self.cal_online:
                    # 
                    RR = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(tmp_objpoints))]
                    TT = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(len(tmp_objpoints))]
                    if self.camera_type == 'omni-radtan':
                        # omni-radtan相机标定
                        try:
                            rms, K, xi, D, RR, TT, idx = cv2.omnidir.calibrate(
                                tmp_objpoints, 
                                tmp_imgpoints,
                                gray.shape[:2][::-1],
                                K=None, xi=None, D=None, flags=flags_omni,
                                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 200, 0.0001)
                            )
                        except Exception:
                            pass
                    elif self.camera_type == 'pinhole-equi':
                        # 鱼眼相机标定
                        rms, K, D, RR, TT = cv2.fisheye.calibrate(
                            tmp_objpoints,
                            tmp_imgpoints,
                            gray.shape[:2][::-1],
                            K=None, D=None, rvecs=RR, tvecs=TT#, flags_fisheye, ctiteria
                        )
                        P = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, gray.shape[:2][::-1], None)
                    elif self.camera_type == 'pinhole-radtan':
                        # 针孔相机标定
                        rms, K, D, RR, TT = cv2.calibrateCamera(
                            tmp_objpoints,
                            tmp_imgpoints,
                            gray.shape[:2][::-1],
                            cameraMatrix=None, distCoeffs=None, rvecs=RR, tvecs=TT
                        )
                    if self.prepare_to_shoot:
                        self.K = np.copy(K)
                        self.D = np.copy(D)
                        self.xi = np.copy(xi)
                        self.prepare_to_shoot = False
                        sig_d = {"K":self.K, "D":self.D, "xi":self.xi}
                        self.signal_para.emit(sig_d)
                    # print(self.K)
                    # print(self.D)
                    rot = cv2.Rodrigues(RR[-1].reshape((3,)))
                    rot_trans = np.matrix([
                        [1,0,0],[0,0,1],[0,-1,0]
                        ])
                    rot = rot[0]
                    r = list(Rotation.from_matrix(rot).as_quat())
                    t = list(TT[-1].reshape((3,)) - TT[0].reshape((3,)))
                    pos = {
                        'q': r,
                        't': t
                    }
                    self.signal_pos.emit(pos)
                elif self.prepare_to_shoot:
                    self.prepare_to_shoot = False
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
                if self.undistort_type == 5:
                    # 仅透视图
                    frame = frame_undistort
                elif self.undistort_type == 4:
                    # 原图
                    frame = frame
                elif self.camera_type == 'omni-radtan' and self.undistort_type > 0:
                    # omni-radtan 不叠加
                    frame = frame_undistort
                else:
                    # 其余皆叠加
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

class PosItemWidget(QWidget):
    def __init__(self, size=QSize(200, 200), parent=None):
        super(PosItemWidget, self).__init__(parent)
        self.resize(size)
        self.setupUi()
    
    def setupUi(self):
        self.combox = QComboBox()
        self.combox.addItems(['欧拉角', '四元数'])
        self.labelx = QLabel("x: r[deg], t[mm]")
        self.labely = QLabel("y: r[deg], t[mm]")
        self.labelz = QLabel("z: r[deg], t[mm]")
        self.labelw = QLabel("w: r[deg], t[mm]")
        self.spinbox_x = QDoubleSpinBox()
        self.spinbox_y = QDoubleSpinBox()
        self.spinbox_z = QDoubleSpinBox()
        self.spinbox_w = QDoubleSpinBox()

        self.spinbox_tx = QDoubleSpinBox()
        self.spinbox_ty = QDoubleSpinBox()
        self.spinbox_tz = QDoubleSpinBox()
        self.spinbox_x.setMinimum(-180)
        self.spinbox_y.setMinimum(-180)
        self.spinbox_z.setMinimum(-180)
        self.spinbox_w.setMinimum(-180)
        self.spinbox_tx.setMinimum(-10000)
        self.spinbox_ty.setMinimum(-10000)
        self.spinbox_tz.setMinimum(-10000)
        self.spinbox_x.setMaximum(180)
        self.spinbox_y.setMaximum(180)
        self.spinbox_z.setMaximum(180)
        self.spinbox_w.setMaximum(180)
        self.spinbox_tx.setMaximum(10000)
        self.spinbox_ty.setMaximum(10000)
        self.spinbox_tz.setMaximum(10000)
        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(self.labelx)
        hlayout1.addWidget(self.spinbox_x)
        hlayout1.addWidget(self.spinbox_tx)
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.labely)
        hlayout2.addWidget(self.spinbox_y)
        hlayout2.addWidget(self.spinbox_ty)
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.labelz)
        hlayout3.addWidget(self.spinbox_z)
        hlayout3.addWidget(self.spinbox_tz)
        hlayout4 = QHBoxLayout()
        hlayout4.addWidget(self.labelw)
        hlayout4.addWidget(self.spinbox_w)
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.combox)
        vlayout.addLayout(hlayout1)
        vlayout.addLayout(hlayout2)
        vlayout.addLayout(hlayout3)
        vlayout.addLayout(hlayout4)
        self.setLayout(vlayout)


class ImageListWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageListWidget, self).__init__(parent)
        self.resize(110, 768)
        self.setupUi()
        self.row_last = 0
    
    def setupUi(self):
        self.icontable = QTableWidget()
        self.icontable.setColumnCount(2)
        self.icontable.setColumnWidth(0, 200)
        self.icontable.setColumnWidth(1, 300)
        self.icontable.horizontalHeader().setVisible(False)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.icontable)

        self.setLayout(hlayout)

    def clear(self):
        self.row_last = 0
        self.icontable.clear()

    def get_item(self):
        combox = QComboBox()
        combox.addItems(['欧拉角', '四元数'])
        # hlayout = QHBoxLayout()
        # hlayout.addWidget(combox)
        return combox

    def addItem(self, file_name):
        exif = piexif.load(file_name)
        thumbnail = exif.pop('thumbnail')
        if thumbnail is not None:
            pix = QPixmap()
            
            pix.loadFromData(thumbnail, "JPG")
        else:
            pix = QPixmap()
            pix.load(file_name)

        pix_scaled = pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label = QLabel("")
        label.setPixmap(pix_scaled)
        self.icontable.insertRow(self.row_last)
        self.icontable.setCellWidget(self.row_last, 0, label)
        # self.icontable.setItem(self.row_last, 1, QTableWidgetItem("123"))
        pos = PosItemWidget(QSize(300, pix_scaled.size().height()))
        self.icontable.setCellWidget(self.row_last, 1, pos)
        self.icontable.setRowHeight(self.row_last, pix_scaled.size().height())
        self.row_last = self.row_last + 1
        self.icontable.scrollToBottom()
    
    def get_pos(self):
        quats = np.zeros((self.icontable.rowCount(), 4))
        trans = np.zeros((self.icontable.rowCount(), 3))
        for row in range(self.icontable.rowCount()):
            trans[row, :] = np.array([
                self.icontable.cellWidget(row, 1).spinbox_tx.value(),
                self.icontable.cellWidget(row, 1).spinbox_ty.value(),
                self.icontable.cellWidget(row, 1).spinbox_tz.value()
            ])
            if self.icontable.cellWidget(row, 1).combox.currentText() == '欧拉角':
                x = self.icontable.cellWidget(row, 1).spinbox_x.value()
                y = self.icontable.cellWidget(row, 1).spinbox_y.value()
                z = self.icontable.cellWidget(row, 1).spinbox_z.value()
                rot_temp = Rotation.from_euler('ZYX', np.array([z, y, x]), degrees=True)
                quats[row, :] = rot_temp.as_quat()
            elif self.icontable.cellWidget(row, 1).combox.currentText() == '四元数':
                x = self.icontable.cellWidget(row, 1).spinbox_x.value()
                y = self.icontable.cellWidget(row, 1).spinbox_y.value()
                z = self.icontable.cellWidget(row, 1).spinbox_z.value()
                w = self.icontable.cellWidget(row, 1).spinbox_w.value()
                q = np.array([x, y, z, w])
                if np.linalg.norm(q) == 0:
                    w = 1
                    q = np.array([0, 0, 0, 1])
                self.icontable.cellWidget(row, 1).spinbox_x.setValue(x / np.linalg.norm(q))
                self.icontable.cellWidget(row, 1).spinbox_y.setValue(y / np.linalg.norm(q))
                self.icontable.cellWidget(row, 1).spinbox_z.setValue(z / np.linalg.norm(q))
                self.icontable.cellWidget(row, 1).spinbox_w.setValue(w / np.linalg.norm(q))
                rot_temp = Rotation.from_quat(np.array([x, y, z, w]))
                quats[row, :] = rot_temp.as_quat()
        rot = Rotation.from_quat(quats)
        return rot, trans

class camviewDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(camviewDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.iconlist = ImageListWidget()
        self.verticalLayout_imagelist.addWidget(self.iconlist)
        for camera_type in camera_type_list:
            self.comboBox.addItem(camera_type)
        self.comboBox_mask.addItems(['无', '短边', '长边'])
        self.radioButtonHGDL.setChecked(False)
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
        self.pushButton_3.clicked.connect(self.on_push_shoot)
        self.pushButton_calonce.clicked.connect(self.on_click_cal_once)
        self.pushButton_project.clicked.connect(self.on_project)
        self.checkBox.toggled.connect(self.on_toggle_points)
        self.horizontalSlider.valueChanged.connect(self.on_change_expose)

        self.cap = None

        self.reopen()
    
    def on_change_expose(self, camera_expose):
        # camera_expose = self.horizontalSlider.value()
        if self.cap is not None:
            self.cap.setExpose(camera_expose)

    def on_toggle_points(self, checked):
        if not self.radioButtonHGDL.isChecked():
            return
        if self.cap is None:
            return
        if hasattr(self.cap, 'enableDraw'):
            self.cap.enableDraw(checked)

    def on_project(self):
        rot, trans = self.iconlist.get_pos()
        err = self.cam.project(rot, trans)
        self.doubleSpinBox_err.setValue(err)

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
        
        self.iconlist.clear()
        
        camera_type = self.comboBox.currentText()
        camera_expose = self.horizontalSlider.value()
        camera_id = self.spinBox_cameraid.value()
        chessboard_corner_x = self.spinBox_cornerx.value()
        chessboard_corner_y = self.spinBox_cornery.value()
        chessboard_size = self.spinBox_size.value()
            
        if self.cap is None:
            if self.radioButtonHGDL.isChecked():
                cameraIdx = self.spinBox_cameraid_2.value()
                self.label_3.setText(QtCore.QCoreApplication.translate("Dialog", "阈值"))
                self.cap = NOKOVCamera(cameraIdx)
                # self.cap.setExpose(camera_expose)
                self.cap.enableDraw(self.checkBox.isChecked())
            else:
                self.label_3.setText(QtCore.QCoreApplication.translate("Dialog", "曝光时间"))
                self.cap = cv2.VideoCapture(camera_id)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, camera_expose)
            self.lineEditWidth.setText(str(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))))
            self.lineEditHeight.setText(str(int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        else:
            self.cap = None
            if self.radioButtonHGDL.isChecked():
                cameraIdx = self.spinBox_cameraid_2.value()
                self.cap = NOKOVCamera(cameraIdx)
                self.label_3.setText(QtCore.QCoreApplication.translate("Dialog", "阈值"))
                # self.cap.setExpose(camera_expose)
                self.cap.enableDraw(self.checkBox.isChecked())
            else:
                self.label_3.setText(QtCore.QCoreApplication.translate("Dialog", "曝光时间"))
                self.cap = cv2.VideoCapture(camera_id)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, camera_expose)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.lineEditWidth.text()))
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.lineEditHeight.text()))
        self.cam = camCalibrateUtil(self.cap, chessboard_size, chessboard_corner_x, chessboard_corner_y)
        self.cam.mask_type = self.comboBox_mask.currentIndex()
        self.cam.gen_mask()
        self.cam.camera_type = camera_type
        self.cam.signal_file.connect(self.add_image)
        self.cam.signal_image.connect(self.show_image)
        self.cam.signal_pos.connect(self.change_pos)
        self.cam.signal_para.connect(self.refresh_para)

        self.cam.start()

    def refresh_para(self, sig_d):
        self.doubleSpinBox_kfx.setValue(sig_d["K"][0, 0])
        self.doubleSpinBox_kfy.setValue(sig_d["K"][1, 1])
        self.doubleSpinBox_kcx.setValue(sig_d["K"][0, 2])
        self.doubleSpinBox_kcy.setValue(sig_d["K"][1, 2])

        self.doubleSpinBox_dk1.setValue(sig_d["D"][0][0])
        self.doubleSpinBox_dk2.setValue(sig_d["D"][0][1])
        self.doubleSpinBox_dp1.setValue(sig_d["D"][0][2])
        self.doubleSpinBox_dp2.setValue(sig_d["D"][0][3])

        self.doubleSpinBox_xi.setValue(sig_d["D"][0][3])
       

    def on_click_cal_once(self):
        self.cam.cal_once()

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

    def on_push_shoot(self):
        self.cam.prepare_to_shoot = True

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
            self.cam.stop()
            self.cam.quit()
            self.cam.waite()
        return super().keyPressEvent(event)

    def closeEvent(self, event):
        self.cam.stop()
        self.cam.quit()
        self.cam.wait()

    def change_pos(self, pos):
        self.camerapos.add_pose([0,0,0], pos['q'])

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




