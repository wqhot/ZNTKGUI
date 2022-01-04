# -*- coding: utf-8 -*-
import cv2
import numpy as np
import sys
import time
from pyqtgraph import plot
from pyqtgraph.functions import disconnect
import yaml
import random
import os
import math
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QListWidget, QDoubleSpinBox, QSpinBox, QWidget, QLabel, QApplication, QListView, QHBoxLayout, QVBoxLayout, QListWidgetItem, QDialog, QFileDialog, QTableWidget, QTableWidgetItem
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Slerp
from scipy.special import comb
from scipy.interpolate import make_interp_spline
from plotCamera import PlotCamera
from ui.Ui_vitualcam import Ui_Dialog
from plotUtils import plotUtils


class virtualCAM(QThread):
    signal_pos = pyqtSignal(dict)
    signal_image = pyqtSignal(object)
    signal_milestone = pyqtSignal(int)
    signal_cam_pos = pyqtSignal(dict)
    singal_change_campos = pyqtSignal(dict)

    def __init__(self, step=0.01, img_step=16):
        super(virtualCAM, self).__init__()
        self.step = step
        self.img_step = img_step
        self.rot = Rotation.from_quat(np.array([0., 0., 0., 1.]))
        self.pos = np.array([0., 0., 0.])
        self.t = [0.]
        self.milestone = np.array([0.])

        self.cam_rot = Rotation.from_euler('ZYX', [0, 0, 0], degrees=True)
        self.cam_pos = np.array([0.0, 0.0, 0.0])

        self.img_shape = (int(1080), int(1920))
        self.mask = None
        # 0 无 1 短边 2 长边
        self.mask_type = 2
        self.camera_type = 'pinhole-radtan'
        self.undistort_type = 0

        self.K = np.zeros((3, 3))
        self.xi = np.zeros((1, 1))
        self.D = np.zeros((4, 1))

        self.wbais_head = np.zeros((3,))
        self.wbais_car = np.zeros((3,))
        self.abais_head = np.zeros((3,))
        self.abais_car = np.zeros((3,))

        self.objpoint = np.zeros((1, 5, 3), dtype=np.float32)
        self.objpoint[0, 0, :] = np.array([0.066275251, 0.073340542, 0.025856482])
        self.objpoint[0, 1, :] = np.array([0.002848404, 0.062531643, 0.008056358])
        self.objpoint[0, 2, :] = np.array([0, 0.019147298, 0.004942755])
        self.objpoint[0, 3, :] = np.array([0.069900446, 0, 0.021058054])
        self.objpoint[0, 4, :] = np.array([0.13414017, 0.000504125, 0])

        self.objcolor = np.zeros((self.objpoint.shape[1], 3))
        self.objcolor[0, :] = np.array([1.0, 0.0, 0.0])
        self.objcolor[1, :] = np.array([0.0, 1.0, 0.0])
        self.objcolor[2, :] = np.array([0.8, 0.5, 0.2])
        self.objcolor[3, :] = np.array([0.0, 0.5, 1.0])
        self.objcolor[4, :] = np.array([0.3, 0.1, 1.0])
        
        # self.objpoint[0, 4, :] = np.array([0.10316, 0.0, 0.5])

    def set_cam(self, file_name):
        with open(file_name,  encoding='utf-8') as f:
            yaml_cfg = yaml.load(f, Loader=yaml.FullLoader)
            l_parameters = yaml_cfg.get("l_parameters")
            k1 = l_parameters.get("k1", 0.0)
            k2 = l_parameters.get("k2", 0.0)
            p1 = l_parameters.get("p1", 0.0)
            p2 = l_parameters.get("p2", 0.0)
            xi = l_parameters.get("xi", 0.0)
            fx = l_parameters.get("fx", 0.0)
            fy = l_parameters.get("fy", 0.0)
            cx = l_parameters.get("cx", 0.0)
            cy = l_parameters.get("cy", 0.0)

            self.wbais_car[0] = yaml_cfg.get("gxmean_no_cam", 0.0)
            self.wbais_car[1] = yaml_cfg.get("gymean_no_cam", 0.0)
            self.wbais_car[2] = yaml_cfg.get("gzmean_no_cam", 0.0)
            self.wbais_head[0] = yaml_cfg.get("gxmean_with_cam", 0.0)
            self.wbais_head[1] = yaml_cfg.get("gymean_with_cam", 0.0)
            self.wbais_head[2] = yaml_cfg.get("gzmean_with_cam", 0.0)

            self.K[0, 0] = fx
            self.K[0, 2] = cx
            self.K[1, 1] = fy
            self.K[1, 2] = cy
            self.K[2, 2] = 1.0

            self.xi[0] = xi
            self.D[0] = k1
            self.D[1] = k2
            self.D[2] = p1
            self.D[3] = p2

    def project(self, objpoints):
        rvecs = -self.cam_rot.as_rotvec()
        tvecs = -np.inner(np.matrix(self.cam_rot.as_matrix()).I, self.cam_pos)
        mean_error = 0
        if self.camera_type == 'omni-radtan':
            # omni-radtan相机反投影
            img_points, _ = cv2.omnidir.projectPoints(
                objpoints,
                rvecs[:],
                tvecs[:],
                K=self.K, xi=self.xi[0][0], D=self.D
            )
            undistort_img_points = cv2.omnidir.undistortPoints(
                img_points,
                self.K, self.D, self.xi, np.eye(3)
            )
        elif self.camera_type == 'pinhole-equi':
            # 鱼眼相机反投影
            img_points, _ = cv2.fisheye.projectPoints(
                objpoints,
                rvecs[:],
                tvecs[:],
                K=self.K, D=self.D
            )
            undistort_img_points = cv2.fisheye.undistortPoints(
                img_points,
                self.K, self.D
            )
        elif self.camera_type == 'pinhole-radtan':
            # 针孔相机反投影
            img_points, _ = cv2.projectPoints(
                objpoints,
                rvecs[:],
                tvecs[:],
                cameraMatrix=self.K,
                distCoeffs=self.D
            )
            undistort_img_points = cv2.undistortPoints(
                img_points,
                self.K, self.D
            )

        return [img_points, undistort_img_points]

    def change_cam_pose(self, rotmat, t):
        self.cam_rot = Rotation.from_matrix(rotmat)
        self.cam_pos = t.astype(np.float32)
        self.gen_image()
        pos = {
            'q': self.cam_rot.as_quat(),
            't': self.cam_pos,
        }
        self.singal_change_campos.emit(pos)

    def pnp(self, undistort_imgpoints):
        K = np.eye(3)
        D = np.zeros((4, 1))
        try:
            retval, rvec, tvec = cv2.solvePnP(
                self.objpoint,
                undistort_imgpoints,
                K, D, flags=cv2.SOLVEPNP_ITERATIVE
            )
            rot = cv2.Rodrigues(rvec.reshape((3,)))
            eul = Rotation.from_matrix(rot[0]).as_euler(
                'ZYX', degrees=True)[::-1]
        except:
            eul = np.zeros((3,))
        return eul

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
        x_dist = np.matrix(
            (np.arange(0, self.img_shape[1], 1, dtype=np.float64) - c[1]) ** 2)
        x_dist = np.repeat(x_dist, self.img_shape[0], axis=0)
        y_dist = np.matrix(
            (np.arange(0, self.img_shape[0], 1, dtype=np.float64) - c[0]) ** 2).T
        y_dist = np.repeat(y_dist, self.img_shape[1], axis=1)
        dist = np.sqrt(x_dist + y_dist)
        self.mask[dist < l] = 1

    # 生成旋转插值 时间精度为steps
    def gen_rot_slerp(self, t, rot):
        rot = np.array(rot)
        key_rots = np.zeros(shape=(len(t), 4), dtype=float)
        key_rots[:, 3] = 1.0
        key_times = np.zeros(shape=(len(t), ), dtype=float)
        for i in range(len(t)):
            if np.linalg.norm(rot[i, :]) == 0:
                continue
            key_rots[i, :] = rot[i, :]
            key_times[i] = t[i]
        key_rots = Rotation.from_quat(key_rots)
        times_slerp = np.linspace(0, t[-1], num=int(t[-1]/self.step))
        slerp = Slerp(times=key_times, rotations=key_rots)
        interp_rots = slerp(times_slerp)
        self.rot = interp_rots
        self.t = times_slerp
        self.milestone = t
        return interp_rots

    def bernstein_poly(self, i, n, t):
        """
        The Bernstein polynomial of n, i as a function of t
        """

        return comb(n, i) * (t**(n-i)) * (1 - t)**i

    # 贝塞尔拟合
    def bezier_curve(self, t, points):
        # 先插值
        times_interp = np.linspace(0, t[-1], num=int(t[-1]/self.step))
        x_interp = np.interp(times_interp, t, points[:, 0])
        y_interp = np.interp(times_interp, t, points[:, 1])
        z_interp = np.interp(times_interp, t, points[:, 2])

        nPoints = len(x_interp)
        nTimes = nPoints
        xPoints = np.array([p[0] for p in points])
        yPoints = np.array([p[1] for p in points])
        zPoints = np.array([p[2] for p in points])

        t = np.linspace(0.0, 1.0, nTimes)

        polynomial_array = np.array([self.bernstein_poly(
            i, nPoints-1, t) for i in range(0, nPoints)])

        xvals = np.dot(x_interp, polynomial_array)[::-1]
        yvals = np.dot(y_interp, polynomial_array)[::-1]
        zvals = np.dot(z_interp, polynomial_array)[::-1]
        point_interp = np.vstack(
            (xvals, yvals, zvals)).T
        self.pos = point_interp
        self.t = times_interp
        self.milestone = t
        return point_interp

    # 平滑插值
    def interp_pos(self, t, points, step=None, setpos=True):
        if step is None:
            step = self.step
        times_interp = np.linspace(0, t[-1], num=int(t[-1] / step))
        k = min(3, len(t) - 1)
        x_spline = make_interp_spline(t, points[:, 0], k=k)
        y_spline = make_interp_spline(t, points[:, 1], k=k)
        z_spline = make_interp_spline(t, points[:, 2], k=k)

        x_interp = x_spline(times_interp)
        y_interp = y_spline(times_interp)
        z_interp = z_spline(times_interp)

        point_interp = np.vstack(
            (x_interp, y_interp, z_interp)).T
        if setpos:
            self.pos = point_interp
            self.t = times_interp
            self.milestone = t
        return point_interp

    def interp_t(self, t):
        times_interp = np.linspace(0, t[-1], num=int(t[-1]/self.step))
        self.t = times_interp
        self.milestone = t
        return times_interp

    def clamp(self, pv):
        if pv > 255:
            return 255
        elif pv < 0:
            return 0
        else:
            return pv

    def gaussian_noise(self, img):
        image = img
        h, w = image.shape
        for row in range(h):
            for col in range(w):
                # 获取三个高斯随机数
                # 第一个参数：概率分布的均值，对应着整个分布的中心
                # 第二个参数：概率分布的标准差，对应于分布的宽度
                # 第三个参数：生成高斯随机数数量
                s = np.random.normal(0, 20, 3)
                # 获取每个像素点的bgr值
                b = image[row, col]  # blue
                # 给每个像素值设置新的bgr值
                image[row, col] = self.clamp(b + s[0])

        return image

    def gen_random(self, img):
        count = random.randint(0, 4)
        for i in range(count):
            center = (random.randint(
                0, img.shape[0]), random.randint(0, img.shape[1]))
            axes = (random.randint(
                0, img.shape[0] / 10), random.randint(0, img.shape[1] / 10))
            angle = random.randint(0, 180)
            color = random.randint(0, 255)
            img = cv2.ellipse(img, center, axes, angle, 0, 360, color, -1)
        # img = self.gaussian_noise(img)
        return img

    def gen_image(self, rotmat=np.matrix(np.identity(3)), t=np.zeros((3,))):
        objpoints = np.copy(self.objpoint)
        for row in range(self.objpoint.shape[1]):
            objpoints[0, row, :] = np.dot(rotmat, objpoints[0, row, :]) + t
        imgpoints, undistort_imgpoints = self.project(objpoints)
        img = np.zeros(shape=(self.img_shape[0], self.img_shape[1], 3), dtype=np.uint8)
        img2 = np.zeros(shape=(self.img_shape[0], self.img_shape[1], 3), dtype=np.uint8)
        for k in range(imgpoints.shape[0]):
            if imgpoints[k, 0, :][0] > 0 and imgpoints[k, 0, :][1] > 0 and imgpoints[k, 0, :][0] < self.img_shape[0] and imgpoints[k, 0, :][1] < self.img_shape[1]:
                img = cv2.circle(
                    img=img,
                    center=(int(imgpoints[k, 0, :][0]),
                            int(imgpoints[k, 0, :][1])),
                    radius=6,
                    color=self.objcolor[k]*255,
                    thickness=-1
                )
                img2 = cv2.circle(
                    img=img2,
                    center=(int(imgpoints[k, 0, :][0]),
                            int(imgpoints[k, 0, :][1])),
                    radius=6,
                    color=(255, 255, 255),
                    thickness=-1
                )
            # cv2.circle(img, imgpoints[0, i, :], 4, 255, -1)
        # img = self.gen_random(img)
        img = cv2.bitwise_and(img, img, mask=self.mask)
        self.signal_image.emit(img)
        return [img2, imgpoints, undistort_imgpoints]

    def run(self):
        bag_name = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        csv_name = './virtual_bag/' + bag_name
        answer_csv_name = './virtual_bag/' + bag_name + '.csv'
        if not os.path.exists(csv_name):
            os.makedirs(csv_name)
        imu_csv_name = csv_name + '/imu_msg.csv'
        img_csv_name = csv_name + '/img_msg.csv'
        points_csv_name = csv_name + '/points.csv'
        start_stamp = time.time()
        imu_f = open(imu_csv_name, 'w')
        img_f = open(img_csv_name, 'w')
        points_f = open(points_csv_name, 'w')
        answer_f = open(answer_csv_name, 'w')
        imu_f.write(
            ',seq,stamp,gx,gy,gz,ax,ay,az,gx_car,gy_car,gz_car,ax_car,ay_car,az_car\n')
        img_f.write(',seq,stamp,img_path\n')
        points_f.write(',seq,pts,pts_undistort\n')
        answer_f.write('stamp,x_ang_cl,z_ang_cl,y_ang_cl,x_pos,y_pos,z_pos\n')
        last_mile = -1
        print('run...')
        real_eul = None
        last_cam_eul = np.array([0, 0, 0])
        for i in range(len(self.t)):
            pos = {
                'q': self.rot.as_quat()[i, :],
                't': self.pos[i, :],
                'progress': int((i + 1) / len(self.t) * 100)
            }
            self.signal_pos.emit(pos)
            # 里程碑判断
            mile = np.where(self.milestone >= self.t[i])[0][0]
            if mile != last_mile:
                last_mile = mile
                self.signal_milestone.emit(mile)
            # 求解角速度
            q_now = self.rot[i].as_quat()
            if i > 0:
                q_last = self.rot[i-1].as_quat()
            else:
                q_last = q_now
            q_diff = 2 * (q_now - q_last) / self.step
            q_conj = np.array([-q_now[0], -q_now[1], -q_now[2], q_now[3]])
            w = np.zeros(shape=(3,))
            w[0] = q_diff[0] * q_conj[3] + q_diff[3] * q_conj[0] - \
                q_diff[2] * q_conj[1] + q_diff[1] * q_conj[2]
            w[1] = q_diff[1] * q_conj[3] + q_diff[3] * q_conj[1] - \
                q_diff[0] * q_conj[2] + q_diff[2] * q_conj[0]
            w[2] = q_diff[2] * q_conj[3] + q_diff[3] * q_conj[2] - \
                q_diff[1] * q_conj[0] + q_diff[0] * q_conj[1]
            w_head = w + self.wbais_head
            w_car = self.wbais_car
            # 求解加速度
            a = np.zeros(shape=(3,))
            p_now = self.pos[i, :]
            if i > 0:
                p_last = self.pos[i-1, :]
            else:
                p_last = p_now
            if i > 1:
                p_last_last = self.pos[i - 2, :]
            else:
                p_last_last = p_last
            v_now = (p_now - p_last) / self.step
            v_last = (p_last - p_last_last) / self.step
            a = (v_now - v_last) / self.step
            a = self.rot[i].apply(a)
            a_head = a + self.abais_head
            a_car = self.abais_car

            eul_now = self.rot[i].as_euler('ZYX', degrees=True)[::-1]
            pos_now = self.pos[i, :]
            if real_eul is None:
                real_eul = np.array([eul_now[0], eul_now[1], eul_now[2], i])
            else:
                real_eul = np.vstack(
                    (real_eul, np.array([eul_now[0], eul_now[1], eul_now[2], i])))
            if i % self.img_step == 0:
                img, imgpoints, undistort_imgpoints = self.gen_image(
                    self.rot[i].as_matrix(), self.pos[i, :])
                cv2.imwrite(
                    csv_name + '/{}.jpg'.format(start_stamp + self.t[i]), img)
                img_f.write(',{},{},~/output/{}/{}.jpg\n'.format(int(i / self.img_step), start_stamp +
                            self.t[i], bag_name, start_stamp + self.t[i]))
                pts_str = ''
                pts_undistort = ''
                for k in range(imgpoints.shape[1]):
                    pts_str = pts_str + \
                        "{}|{}|".format(imgpoints[0, k, 0], imgpoints[0, k, 1])
                    pts_undistort = pts_undistort + \
                        "{}|{}|".format(
                            undistort_imgpoints[0, k, 0], undistort_imgpoints[0, k, 1])
                points_f.write(',{},{},{}\n'.format(
                    int(i / self.img_step), pts_str, pts_undistort))
                cam_eul = self.pnp(undistort_imgpoints)
                cam_eul = cam_eul.reshape((1, 3))
                points_2_interp = np.vstack((last_cam_eul, cam_eul))
                if i != 0:
                    cam_eul_interp = self.interp_pos(
                        np.array([0, self.img_step]), points_2_interp, 1, False)
                else:
                    cam_eul_interp = cam_eul
                # print(cam_eul_interp.shape)
                self.signal_cam_pos.emit({'eul': cam_eul_interp})
                last_cam_eul = cam_eul
            imu_f.write(',{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                i, start_stamp + self.t[i],
                w_head[0], w_head[1], w_head[2],
                a_head[0], a_head[1], a_head[2],
                w_car[0], w_car[1], w_car[2],
                a_car[0], a_car[1], a_car[2]
            ))

            answer_f.write('{},{},{},{},{},{},{}\n'.format(
                start_stamp + self.t[i], eul_now[0], eul_now[2], eul_now[1], pos_now[0], pos_now[1], pos_now[2]))
            time.sleep(self.step * 10)
        imu_f.close()
        img_f.close()
        points_f.close()
        print('over')


class PosItemWidget(QWidget):
    def __init__(self, t=0, size=QSize(200, 200), parent=None):
        super(PosItemWidget, self).__init__(parent)
        self.resize(size)
        self.setupUi(t)

    def setupUi(self, t=0):
        self.combox = QComboBox()
        self.combox.addItems(['欧拉角', '四元数'])
        self.labelx = QLabel("x: r[deg], t[mm]")
        self.labely = QLabel("y: r[deg], t[mm]")
        self.labelz = QLabel("z: r[deg], t[mm]")
        self.labelw = QLabel("w: r[deg], t[mm]")
        self.labelt = QLabel("t: [s]")
        self.spinbox_x = QDoubleSpinBox()
        self.spinbox_y = QDoubleSpinBox()
        self.spinbox_z = QDoubleSpinBox()
        self.spinbox_w = QDoubleSpinBox()

        self.spinbox_tx = QDoubleSpinBox()
        self.spinbox_ty = QDoubleSpinBox()
        self.spinbox_tz = QDoubleSpinBox()
        self.spinbox_t = QDoubleSpinBox()
        self.spinbox_x.setMinimum(-180)
        self.spinbox_y.setMinimum(-180)
        self.spinbox_z.setMinimum(-180)
        self.spinbox_w.setMinimum(-180)
        self.spinbox_tx.setMinimum(-10000)
        self.spinbox_ty.setMinimum(-10000)
        self.spinbox_tz.setMinimum(-10000)
        self.spinbox_t.setMinimum(t)
        self.spinbox_x.setMaximum(180)
        self.spinbox_y.setMaximum(180)
        self.spinbox_z.setMaximum(180)
        self.spinbox_w.setMaximum(180)
        self.spinbox_tx.setMaximum(10000)
        self.spinbox_ty.setMaximum(10000)
        self.spinbox_tz.setMaximum(10000)
        self.spinbox_t.setMaximum(10000)
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
        hlayout5 = QHBoxLayout()
        hlayout5.addWidget(self.labelt)
        hlayout5.addWidget(self.spinbox_t)
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.combox)
        vlayout.addLayout(hlayout1)
        vlayout.addLayout(hlayout2)
        vlayout.addLayout(hlayout3)
        vlayout.addLayout(hlayout4)
        vlayout.addLayout(hlayout5)
        self.setLayout(vlayout)

    def setup_value(self, c, x, y, z, w, tx, ty, tz, t):
        self.combox.setCurrentIndex(c)
        self.spinbox_x.setValue(x)
        self.spinbox_y.setValue(y)
        self.spinbox_z.setValue(z)
        self.spinbox_w.setValue(w)
        self.spinbox_tx.setValue(tx)
        self.spinbox_ty.setValue(ty)
        self.spinbox_tz.setValue(tz)
        self.spinbox_t.setValue(t)


class PosTableWidget(QWidget):
    def __init__(self, parent=None):
        super(PosTableWidget, self).__init__(parent)
        # self.resize(110, 768)
        self.setupUi()
        self.row_last = 0

    def setupUi(self):
        self.icontable = QTableWidget()
        self.icontable.setColumnCount(2)
        self.icontable.setColumnWidth(0, 200)
        self.icontable.setColumnWidth(1, 10)
        self.icontable.horizontalHeader().setVisible(False)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.icontable)

        self.setLayout(hlayout)

    def clear(self):
        self.row_last = 0
        self.icontable.clear()

    def clear_status(self):
        for row in range(self.icontable.rowCount()):
            self.icontable.cellWidget(row, 1).setText('')

    def get_item(self):
        combox = QComboBox()
        combox.addItems(['欧拉角', '四元数'])
        # hlayout = QHBoxLayout()
        # hlayout.addWidget(combox)
        return combox

    def addItem(self):
        self.icontable.insertRow(self.row_last)
        # self.icontable.setCellWidget(self.row_last, 0, label)
        t = 0
        if self.row_last > 0:
            t = self.icontable.cellWidget(
                self.row_last - 1, 0).spinbox_t.value() + 0.01
        pos = PosItemWidget(t, QSize(300, 200))
        if self.row_last > 0:
            pos.setup_value(
                self.icontable.cellWidget(
                    self.row_last - 1, 0).combox.currentIndex(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_x.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_y.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_z.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_w.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_tx.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_ty.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_tz.value(),
                self.icontable.cellWidget(
                    self.row_last - 1, 0).spinbox_t.value() + 0.01
            )
        label = QLabel()
        self.icontable.setCellWidget(self.row_last, 0, pos)
        self.icontable.setCellWidget(self.row_last, 1, label)
        self.icontable.setRowHeight(self.row_last, 200)
        self.row_last = self.row_last + 1
        self.icontable.scrollToBottom()

    def get_pos(self):
        quats = np.zeros((self.icontable.rowCount(), 4))
        trans = np.zeros((self.icontable.rowCount(), 3))
        ts = np.zeros((self.icontable.rowCount(),))
        for row in range(self.icontable.rowCount()):
            trans[row, :] = np.array([
                self.icontable.cellWidget(row, 0).spinbox_tx.value(),
                self.icontable.cellWidget(row, 0).spinbox_ty.value(),
                self.icontable.cellWidget(row, 0).spinbox_tz.value()
            ])
            ts[row] = self.icontable.cellWidget(row, 0).spinbox_t.value()
            if self.icontable.cellWidget(row, 0).combox.currentText() == '欧拉角':
                x = self.icontable.cellWidget(row, 0).spinbox_x.value()
                y = self.icontable.cellWidget(row, 0).spinbox_y.value()
                z = self.icontable.cellWidget(row, 0).spinbox_z.value()
                rot_temp = Rotation.from_euler(
                    'ZYX', np.array([z, y, x]), degrees=True)
                quats[row, :] = rot_temp.as_quat()
            elif self.icontable.cellWidget(row, 0).combox.currentText() == '四元数':
                x = self.icontable.cellWidget(row, 0).spinbox_x.value()
                y = self.icontable.cellWidget(row, 0).spinbox_y.value()
                z = self.icontable.cellWidget(row, 0).spinbox_z.value()
                w = self.icontable.cellWidget(row, 0).spinbox_w.value()
                q = np.array([x, y, z, w])
                if np.linalg.norm(q) == 0:
                    w = 1
                    q = np.array([0, 0, 0, 1])
                self.icontable.cellWidget(
                    row, 0).spinbox_x.setValue(x / np.linalg.norm(q))
                self.icontable.cellWidget(
                    row, 0).spinbox_y.setValue(y / np.linalg.norm(q))
                self.icontable.cellWidget(
                    row, 0).spinbox_z.setValue(z / np.linalg.norm(q))
                self.icontable.cellWidget(
                    row, 0).spinbox_w.setValue(w / np.linalg.norm(q))
                rot_temp = Rotation.from_quat(np.array([x, y, z, w]))
                quats[row, :] = rot_temp.as_quat()
        rot = Rotation.from_quat(quats)
        return rot, trans, ts


class virtualCAMDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super(virtualCAMDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.camerapos = PlotCamera(self.verticalLayout_3d)
        self.iconlist = PosTableWidget()
        self.verticalLayout_table.addWidget(self.iconlist)
        self.virtual = virtualCAM(step=0.001)

        self.plot = plotUtils(
            time_length=30000, layout=self.verticalLayout_plot)
        self.plot.add_line('real x', (0x6b, 0x8e, 0x23), Qt.DashLine)
        self.plot.add_line('real y', (0xee, 0x82, 0xee), Qt.DashLine)
        self.plot.add_line('real z', (0xcc, 0x00, 0x00), Qt.DashLine)

        self.plot.add_line('pnp x', (0x6b, 0x8e, 0x23), Qt.SolidLine)
        self.plot.add_line('pnp y', (0xee, 0x82, 0xee), Qt.SolidLine)
        self.plot.add_line('pnp z', (0xcc, 0x00, 0x00), Qt.SolidLine)

        self.virtual.signal_pos.connect(self.move)
        self.virtual.signal_image.connect(self.show_image)
        self.virtual.signal_milestone.connect(self.on_next_milestone)
        self.virtual.signal_cam_pos.connect(self.on_pnp)
        self.virtual.singal_change_campos.connect(self.on_change_campos)

        self.horizontalSlider_czd.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_cyd.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_cxd.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_czt.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_cyt.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_cxt.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_hfov.valueChanged.connect(
            self.change_cam_pos_by_slider)
        self.horizontalSlider_vfov.valueChanged.connect(
            self.change_cam_pos_by_slider)

        self.doubleSpinBox_cxd.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_cyd.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_czd.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_cxt.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_cyt.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_czt.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_hfov.valueChanged.connect(
            self.change_cam_pos_by_spinbox)
        self.doubleSpinBox_vfov.valueChanged.connect(
            self.change_cam_pos_by_spinbox)

        self.doubleSpinBox_cxt.setValue(0)
        self.doubleSpinBox_cyt.setValue(45)
        self.doubleSpinBox_czt.setValue(30)
        self.change_cam_pos_by_spinbox()

        point_num = self.virtual.objpoint.shape[0] * \
            self.virtual.objpoint.shape[1]
        objpoint = self.virtual.objpoint.reshape((point_num, 3))

        self.pushButton.clicked.connect(self.on_add)
        self.pushButton_2.clicked.connect(self.on_interp)

        directory = QFileDialog.getOpenFileName(self,
                                                "相机参数", "../cam.txt",
                                                "Text Files (*.txt)")
        if len(directory[0]) != 0:
            self.virtual.set_cam(directory[0])

        self.camerapos.hfov = math.atan((self.virtual.img_shape[1] - self.virtual.K[0, 2]) /self.virtual.K[0, 0]) * 180.0 / math.pi + \
                              math.atan((self.virtual.K[0, 2]) /self.virtual.K[0, 0]) * 180.0 / math.pi

        self.camerapos.vfov = math.atan((self.virtual.img_shape[0] - self.virtual.K[1, 2]) /self.virtual.K[1, 1]) * 180.0 / math.pi + \
                              math.atan((self.virtual.K[1, 2]) /self.virtual.K[1, 1]) * 180.0 / math.pi

        self.camerapos.add_pose(self.virtual.cam_pos,
                                self.virtual.cam_rot.as_quat())
        self.camerapos.add_fix_point(objpoint, self.virtual.objcolor)
        self.doubleSpinBox_hfov.setValue(int(self.camerapos.hfov))
        self.doubleSpinBox_vfov.setValue(int(self.camerapos.vfov))
        self.horizontalSlider_hfov.setValue(int(self.camerapos.hfov))
        self.horizontalSlider_vfov.setValue(int(self.camerapos.vfov))
        self.imu_count = 0
        self.pnp_count = 0
        # self.auto_move_cam()

    def auto_move_cam(self):
        cam_position = self.virtual.cam_pos
        point_num = self.virtual.objpoint.shape[0] * \
            self.virtual.objpoint.shape[1]
        objpoint = self.virtual.objpoint.reshape((point_num, 3))
        objcenter = np.average(objpoint, axis=0)
        origin = np.array([0., 0., -1.])
        target = cam_position - objcenter
        target = target / np.linalg.norm(target)
        sita = math.acos(np.dot(target, origin))
        n_vector = np.cross(target, origin)
        n_vector = n_vector / np.linalg.norm(n_vector)
        n_vector_invert = np.matrix(
            [[0, -n_vector[2], n_vector[1]],
             [n_vector[2], 0, -n_vector[0]],
             [-n_vector[1], n_vector[0], 0]
             ]
        )
        R = np.matrix(np.identity(3)) + math.sin(sita) * n_vector_invert + n_vector_invert * n_vector_invert * (1-math.cos(sita))
        R = Rotation.from_matrix(R)
        euler = R.as_euler('ZYX', degrees=True)[::-1]
        self.doubleSpinBox_cxd.setValue(euler[0])
        self.doubleSpinBox_cyd.setValue(euler[1])
        self.doubleSpinBox_czd.setValue(euler[2])
        self.change_cam_pos_by_spinbox()


    def change_cam_pos_by_slider(self):
        self.doubleSpinBox_cxd.setValue(self.horizontalSlider_cxd.value())
        self.doubleSpinBox_cyd.setValue(self.horizontalSlider_cyd.value())
        self.doubleSpinBox_czd.setValue(self.horizontalSlider_czd.value())
        self.doubleSpinBox_cxt.setValue(self.horizontalSlider_cxt.value())
        self.doubleSpinBox_cyt.setValue(self.horizontalSlider_cyt.value())
        self.doubleSpinBox_czt.setValue(self.horizontalSlider_czt.value())
        self.doubleSpinBox_hfov.setValue(int(self.camerapos.hfov))
        self.doubleSpinBox_vfov.setValue(int(self.camerapos.vfov))
        self.change_cam_pose()

    def change_cam_pos_by_spinbox(self):
        self.horizontalSlider_cxd.setValue(self.doubleSpinBox_cxd.value())
        self.horizontalSlider_cyd.setValue(self.doubleSpinBox_cyd.value())
        self.horizontalSlider_czd.setValue(self.doubleSpinBox_czd.value())
        self.horizontalSlider_cxt.setValue(self.doubleSpinBox_cxt.value())
        self.horizontalSlider_cyt.setValue(self.doubleSpinBox_cyt.value())
        self.horizontalSlider_czt.setValue(self.doubleSpinBox_czt.value())
        self.horizontalSlider_hfov.setValue(int(self.camerapos.hfov))
        self.horizontalSlider_vfov.setValue(int(self.camerapos.vfov))
        self.change_cam_pose()

    def change_cam_pose(self):
        rotmat = Rotation.from_euler(
            'ZYX',
            [self.horizontalSlider_czd.value(), self.horizontalSlider_cyd.value(),
             self.horizontalSlider_cxd.value()],
            degrees=True
        ).as_matrix()
        t = np.array([self.doubleSpinBox_cxt.value(
        ) / 100.0, self.doubleSpinBox_cyt.value() / 100.0, self.doubleSpinBox_czt.value() / 100.0])
        self.virtual.change_cam_pose(rotmat, t)

    def on_add(self):
        self.iconlist.addItem()

    def on_interp(self):
        [rot, trans, ts] = self.iconlist.get_pos()
        self.interp_rots = self.virtual.gen_rot_slerp(ts, rot.as_quat())
        self.interp_pos = self.virtual.interp_pos(ts, trans)
        self.interp_t = self.virtual.interp_t(ts)
        self.iconlist.clear_status()
        self.progressBar.setValue(0)
        self.imu_count = 0
        self.pnp_count = 0
        self.virtual.start()

    def show_image(self, img):
        # img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        convertToQtFormat = QtGui.QImage(
            img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        p = convertToQtFormat.scaled(
            self.label_image.width(), self.label_image.height(), Qt.KeepAspectRatio)
        self.label_image.setPixmap(QPixmap.fromImage(p))

    def on_next_milestone(self, milestone):
        self.iconlist.icontable.cellWidget(milestone, 1).setText("√")

    def on_change_campos(self, pos):
        self.camerapos.add_pose(pos['t'], pos['q'])

    def move(self, pos):
        self.camerapos.transform_points(pos['t'], pos['q'])
        q = Rotation.from_quat(pos['q'])
        # print(pos['q'])
        eul = q.as_euler('ZYX', degrees=True)[::-1]
        self.plot.add_data('real x', np.array([eul[0]]))
        self.plot.add_data('real y', np.array([eul[1]]))
        self.plot.add_data('real z', np.array([eul[2]]))
        self.progressBar.setValue(pos['progress'])
        self.imu_count = self.imu_count + 1
        # print("imu_count = {}".format(self.imu_count))

    def on_pnp(self, pos):
        eul = pos['eul']
        self.plot.add_data('pnp x', eul[:, 0])
        self.plot.add_data('pnp y', eul[:, 1])
        self.plot.add_data('pnp z', eul[:, 2])
        self.pnp_count = self.pnp_count + eul.shape[0]
        # print("pnp_count = {}".format(self.pnp_count))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = virtualCAMDialog()
    mainwin.show()
    sys.exit(app.exec_())
