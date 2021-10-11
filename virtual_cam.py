# -*- coding: utf-8 -*-
import cv2
import numpy as np
import sys
import time
import yaml
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QListWidget, QDoubleSpinBox, QSpinBox, QWidget, QLabel, QApplication, QListView, QHBoxLayout, QVBoxLayout, QListWidgetItem, QDialog, QFileDialog, QTableWidget, QTableWidgetItem
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Slerp
from scipy.special import comb
from plotCamera import PlotCamera
from ui.Ui_vitualcam import Ui_Dialog

class virtualCAM(QThread):
    signal_pos = pyqtSignal(dict)
    def __init__(self, step=0.01):
        super(virtualCAM, self).__init__()
        self.step = step
        self.rot = Rotation.from_quat(np.array([0. ,0. ,0., 1.]))
        self.pos = np.array([0., 0., 0.])
        self.t = [0.]
        
        self.img_shape = (int(480), int(640))
        self.mask = None
        # 0 无 1 短边 2 长边
        self.mask_type = 0
        self.camera_type = 'omni-radtan'
        self.undistort_type = 0

        self.K = np.zeros((3, 3))
        self.xi = np.zeros((1, 1))
        self.D = np.zeros((4, 1))

        self.objpoint = np.zeros((1, 6, 3), dtype=np.float32)
        self.objpoint[0, 0, :] = np.array([0.0, -0.3, -0.077])
        self.objpoint[0, 1, :] = np.array([0.0, -0.3, 0.0])
        self.objpoint[0, 2, :] = np.array([0.0, -0.3, 0.07409])
        self.objpoint[0, 3, :] = np.array([0.20632, -0.3, -0.077])
        self.objpoint[0, 4, :] = np.array([0.20632, -0.3, 0.0])
        self.objpoint[0, 5, :] = np.array([0.20632, -0.3, 0.07409])


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

    def project(self, rot, trans):
        rvecs = rot.as_rotvec()
        tvecs = trans
        mean_error = 0
        if self.camera_type == 'omni-radtan':
            # omni-radtan相机反投影
            img_points, _ = cv2.omnidir.projectPoints(
                self.objpoint, 
                rvecs[:],
                tvecs[:],
                K=self.K, xi=self.xi[0][0], D=self.D
            )
        elif self.camera_type == 'pinhole-equi':
            # 鱼眼相机反投影
            img_points, _ = cv2.fisheye.projectPoints(
                self.objpoint, 
                rvecs[:],
                tvecs[:],
                K=self.K, D=self.D
            )
        elif self.camera_type == 'pinhole-radtan':
            # 针孔相机反投影
            img_points, _ = cv2.projectPoints(
                self.objpoint, 
                rvecs[:],
                tvecs[:],
                K=self.K, D=self.D
            )
            
        return img_points
            
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
        return interp_rots

    def bernstein_poly(self, i, n, t):
        """
        The Bernstein polynomial of n, i as a function of t
        """

        return comb(n, i) * ( t**(n-i) ) * (1 - t)**i
    
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

        polynomial_array = np.array([ self.bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

        xvals = np.dot(x_interp, polynomial_array)[::-1]
        yvals = np.dot(y_interp, polynomial_array)[::-1]
        zvals = np.dot(z_interp, polynomial_array)[::-1]
        point_interp = np.vstack(
            (xvals, yvals, zvals)).T
        self.pos = point_interp
        self.t = times_interp
        return point_interp

    def interp_t(self, t):
        times_interp = np.linspace(0, t[-1], num=int(t[-1]/self.step))
        self.t = times_interp
        return times_interp

    def run(self):
        for i in range(len(self.t)):
            pos = {
                'q': self.rot.as_quat()[i, :],
                't': self.pos[i, :]
                }
            self.signal_pos.emit(pos)
            imgpoints = self.project(self.rot[i], self.pos[i, :])
            print(imgpoints)
            img = np.zeros(shape=self.img_shape, dtype=np.uint8)
            for i in range(imgpoints.shape[1]):
                print(imgpoints[0, i, :])
                cv2.circle(img, imgpoints[0, i, :], 4, 255, -1)
            img = cv2.bitwise_and(img, img, mask=self.mask)
            cv2.imwrite('./images/{}.jpg'+self.t[i], img)
            time.sleep(self.step * 10)
        print('over')
            


class PosItemWidget(QWidget):
    def __init__(self, t = 0, size=QSize(200, 200), parent=None):
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

    def addItem(self):
        self.icontable.insertRow(self.row_last)
        # self.icontable.setCellWidget(self.row_last, 0, label)
        t = 0
        if self.row_last > 0:
            t = self.icontable.cellWidget(self.row_last - 1, 0).spinbox_t.value() + 0.01
        pos = PosItemWidget(t, QSize(300, 200))
        if self.row_last > 0:
            pos.setup_value(
                self.icontable.cellWidget(self.row_last - 1, 0).combox.currentIndex(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_x.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_y.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_z.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_w.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_tx.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_ty.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_tz.value(),
                self.icontable.cellWidget(self.row_last - 1, 0).spinbox_t.value() + 0.01
            )
        self.icontable.setCellWidget(self.row_last, 0, pos)
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
                rot_temp = Rotation.from_euler('ZYX', np.array([z, y, x]), degrees=True)
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
                self.icontable.cellWidget(row, 0).spinbox_x.setValue(x / np.linalg.norm(q))
                self.icontable.cellWidget(row, 0).spinbox_y.setValue(y / np.linalg.norm(q))
                self.icontable.cellWidget(row, 0).spinbox_z.setValue(z / np.linalg.norm(q))
                self.icontable.cellWidget(row, 0).spinbox_w.setValue(w / np.linalg.norm(q))
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
        self.virtual = virtualCAM()

        self.virtual.signal_pos.connect(self.move)

        self.pushButton.clicked.connect(self.on_add)
        self.pushButton_2.clicked.connect(self.on_interp)

        directory = QFileDialog.getOpenFileName(self,
                                                "相机参数", "../cam.txt",
                                                "Text Files (*.txt)")
        if len(directory[0]) != 0:
            self.virtual.set_cam(directory[0])

    def on_add(self):
        self.iconlist.addItem()

    def on_interp(self):
        [rot, trans, ts] = self.iconlist.get_pos()
        self.interp_rots = self.virtual.gen_rot_slerp(ts, rot.as_quat())
        self.interp_pos = self.virtual.bezier_curve(ts, trans)
        self.interp_t = self.virtual.interp_t(ts)

        self.virtual.start()
        
    
    def move(self, pos):
        print('get pos')
        self.camerapos.add_pose(pos['t'], pos['q'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwin = virtualCAMDialog()
    mainwin.show()
    sys.exit(app.exec_())