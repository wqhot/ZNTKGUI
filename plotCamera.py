# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from scipy.spatial.transform import Rotation
from config import TIME_LENGTH, SCALE


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

        # self.pos_text = gl.GLTextItem(pos=(0,0,0), text=(0,0,0), font=QtGui.QFont('Helvetica', 7))
        # self.w.addItem(self.pos_text)

        self.imlt = [-0.01, -0.005, -0.01]
        self.imrt = [0.01, -0.005, -0.01]
        self.imlb = [-0.01, 0.005, -0.01]
        self.imrb = [0.01, 0.005, -0.01]
        self.lt0 = [-0.7, -0.5, 1.0]
        self.lt1 = [-0.7, -0.2, 1.0]
        self.lt2 = [-1.0, -0.2, 1.0]
        self.oc = [0.0, 0.0, 0.0]
        self.lines = []
        pos = np.empty((TIME_LENGTH, 3))
        size = np.empty((TIME_LENGTH))
        color = np.empty((TIME_LENGTH, 4))
        self.fix_points = None
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

    def add_fix_point(self, points):
        self.fix_points = gl.GLScatterPlotItem(pos=points, size=0.005, color=(0.0, 1.0, 0.0, 1.0), pxMode=False)
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

    def add_pose(self, p, q):
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
