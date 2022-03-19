# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import math
from scipy.spatial.transform import Rotation
from config import TIME_LENGTH, SCALE
from stl import mesh as stlmesh

class PlotCamera(): 
    def __init__(self, layout):
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 1.0
        # self.w.show()
        # self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 0.1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 0.1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        axis = gl.GLAxisItem()
        axis.setSize(0.2, 0.2, 0.2)
        self.w.addItem(axis)

        # self.x_text = gl.GLTextItem(pos=(0.2,0,0), text="x", font=QtGui.QFont('Helvetica', 7))
        # self.w.addItem(self.x_text)
        # self.y_text = gl.GLTextItem(pos=(0,0.2,0), text="y", font=QtGui.QFont('Helvetica', 7))
        # self.w.addItem(self.y_text)
        # self.z_text = gl.GLTextItem(pos=(0,0,0.2), text="z", font=QtGui.QFont('Helvetica', 7))
        # self.w.addItem(self.z_text)
        self.hfov = 90.0
        self.vfov = 60.0
        self.cam_rotmat = Rotation.from_rotvec([0., 0., 0.])
        self.cam_t = np.array([0., 0., 0.])
        self.max_depth = 0.01 # 相机深度

        self.imlt = [-0.01, -0.005, 0.01]
        self.imrt = [0.01, -0.005, 0.01]
        self.imlb = [-0.01, 0.005, 0.01]
        self.imrb = [0.01, 0.005, 0.01]
        self.oc = [0.0, 0.0, 0.0]
        self.cal_cam_fov()
        self.lines = []
        pos = np.empty((TIME_LENGTH, 3))
        size = np.empty((TIME_LENGTH))
        color = np.empty((TIME_LENGTH, 4))
        self.fix_points = None
        self.points = None
        self.currentSTL = None
        self.showSTL('./res/helmat.stl')
        self.head_last_rot = Rotation.from_quat([0,0,0,1])
        self.head_last_trans = np.array([0., 0., 0.])
        for i in range(TIME_LENGTH):
            pos[i] = (0, 0, 0)
            size[i] = 0.005
            color[i] = (i * 1.0 / TIME_LENGTH, 0.0, 0.0, 1.0)
        self.history = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
        self.w.addItem(self.history)
        for i in range(8):
            self.lines.append(gl.GLLinePlotItem(antialias=True))
            self.w.addItem(self.lines[i])
        layout.addWidget(self.w)
    
    def showSTL(self, filename):
        if self.currentSTL:
            self.w.removeItem(self.currentSTL)

        points, faces = self.loadSTL(filename)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0.4, 0.4, 0.4, 0.001))
        self.w.addItem(mesh)
        self.currentSTL = mesh

    def loadSTL(self, filename):
        m = stlmesh.Mesh.from_file(filename)
        # m.rotate([0, 1.0, 0], math.radians(90))
        # m.rotate([1.0, 0, 0], math.radians(-90))
        # m.rotate([0, 0, 1.0], math.radians(-90))
        # m.x += 0.06
        # m.y += 0.25
        shape = m.points.shape
        points = m.points.reshape(-1, 3) / 1000.0
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces

    def cal_cam_fov(self):
        self.imlt = [-self.max_depth * 2.0 * math.tan(self.hfov * math.pi / 360.0), -self.max_depth * 2.0 * math.tan(self.vfov * math.pi / 360.0), -self.max_depth]
        self.imrt = [ self.max_depth * 2.0 * math.tan(self.hfov * math.pi / 360.0), -self.max_depth * 2.0 * math.tan(self.vfov * math.pi / 360.0), -self.max_depth]
        self.imlb = [-self.max_depth * 2.0 * math.tan(self.hfov * math.pi / 360.0),  self.max_depth * 2.0 * math.tan(self.vfov * math.pi / 360.0), -self.max_depth]
        self.imrb = [ self.max_depth * 2.0 * math.tan(self.hfov * math.pi / 360.0),  self.max_depth * 2.0 * math.tan(self.vfov * math.pi / 360.0), -self.max_depth]

    def add_fix_point(self, points, color):
        self.points = points
        color_ = np.ones((color.shape[0], 4))
        color_[:, :3] = color
        self.fix_points = gl.GLScatterPlotItem(pos=points, size=0.005, color=color_, pxMode=False)
        self.w.addItem(self.fix_points)

    def drawLine(self,index, start, end):
        x = np.linspace(start[0], end[0], 50)
        y = np.linspace(start[1], end[1], 50)
        z = np.linspace(start[2], end[2], 50)
        pts = np.vstack([x,y,z]).transpose()
        self.lines[index].setData(pos=pts) 
        # self.w.addItem(plt)

    def quat_to_euler(self, quat):
        q = np.array(quat)
        R = Rotation.from_quat(q)
        return R.as_euler('ZYX', degrees=True)[::-1]

    def quaternion_to_rotation_matrix(self, quat):
        rot_matrix = Rotation.from_quat(quat).as_matrix()
        return rot_matrix

    def draw_history(self, pos):
        scale = SCALE
        pos = np.vstack(scale * np.array(pos))
        self.history.setData(pos=pos)
    
    def reset(self, p, q):
        self.transform_points(p, q)

    def transform_points(self, p, q):
        rot_matrix = self.quaternion_to_rotation_matrix(q)
        if self.currentSTL:
            rotmat = Rotation.from_quat(q)
            det_rot = rotmat * self.head_last_rot.inv()
            det_trans = p - self.head_last_trans
            rotvec = det_rot.as_rotvec()
            self.currentSTL.rotate(np.linalg.norm(rotvec) * 180.0 / math.pi, rotvec[0], rotvec[1], rotvec[2])
            self.currentSTL.translate(det_trans[0], det_trans[1], det_trans[2])
            self.head_last_trans = p
            self.head_last_rot = rotmat
        points = np.copy(self.points)
        cam_center = np.matmul(self.cam_rotmat.as_matrix(), self.oc) + self.cam_t
        self.max_depth = 0.01
        for row in range(self.points.shape[0]):
            points[row, :] = np.dot(rot_matrix, points[row, :]) + p
            depth = np.linalg.norm(points[row, :] - cam_center) * 1.05
            if depth > self.max_depth:
                self.max_depth = depth
        self.fix_points.setData(pos=points)

    def add_pose(self, p, q):
        self.cam_rotmat = Rotation.from_quat(q)
        self.cam_t = np.array(p)
        self.cal_cam_fov()
        rot_matrix = self.quaternion_to_rotation_matrix(q)
        euler = self.quat_to_euler(q)
        scale = SCALE
        pt_lt = scale * (np.matmul(rot_matrix, self.imlt) + p)
        pt_lb = scale * (np.matmul(rot_matrix, self.imlb) + p)
        pt_rt = scale * (np.matmul(rot_matrix, self.imrt) + p)
        pt_rb = scale * (np.matmul(rot_matrix, self.imrb) + p)
        pt_oc = scale * (np.matmul(rot_matrix, self.oc) + p)
        self.drawLine(0, pt_lt, pt_rt)
        self.drawLine(1, pt_lt, pt_lb)
        self.drawLine(2, pt_lb, pt_rb)
        self.drawLine(3, pt_rb, pt_rt)
        self.drawLine(4, pt_oc, pt_lt)
        self.drawLine(5, pt_oc, pt_lb)
        self.drawLine(6, pt_oc, pt_rb)
        self.drawLine(7, pt_oc, pt_rt)

        # self.pos_text.setData(
        #     # pos = p,
        #     text='({:.1f},{:.1f},{:.1f})'.format(euler[0], euler[1], euler[2])
        #     )
