# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np


class PlotCamera(): 
    def __init__(self, layout):
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 40
        self.w.show()
        # self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        self.imlt = [-1.0, -0.5, 1.0]
        self.imrt = [1.0, -0.5, 1.0]
        self.imlb = [-1.0,  0.5, 1.0]
        self.imrb = [1.0,  0.5, 1.0]
        self.lt0 = [-0.7, -0.5, 1.0]
        self.lt1 = [-0.7, -0.2, 1.0]
        self.lt2 = [-1.0, -0.2, 1.0]
        self.oc = [0.0, 0.0, 0.0]
        self.lines = []
        for i in range(8):
            self.lines.append(gl.GLLinePlotItem(antialias=True))
            self.w.addItem(self.lines[i])
        layout.addWidget(self.w)

    def drawLine(self,index, start, end):
        x = np.linspace(start[0], end[0], 50)
        y = np.linspace(start[1], end[1], 50)
        z = np.linspace(start[2], end[2], 50)
        pts = np.vstack([x,y,z]).transpose()
        self.lines[index].setData(pos=pts) 
        # self.w.addItem(plt)

    def quaternion_to_rotation_matrix(self, quat):
        temp = quat[0]
        quat[0] = quat[1]
        quat[1] = quat[2]
        quat[2] = quat[3]
        quat[3] = temp
        quat = np.array(quat)
        q = quat.copy()
        n = np.dot(q, q)
        if n < np.finfo(q.dtype).eps:
            return np.identity(3)
        q = q * np.sqrt(2.0 / n)
        q = np.outer(q, q)
        rot_matrix = np.array(
            [[1.0 - q[2, 2] - q[3, 3], q[1, 2] + q[3, 0], q[1, 3] - q[2, 0]],
            [q[1, 2] - q[3, 0], 1.0 - q[1, 1] - q[3, 3], q[2, 3] + q[1, 0]],
            [q[1, 3] + q[2, 0], q[2, 3] - q[1, 0], 1.0 - q[1, 1] - q[2, 2]]],
            dtype=q.dtype)
        return rot_matrix


    def add_pose(self, p, q):
        rot_matrix = self.quaternion_to_rotation_matrix(q)
        scale = 3.0
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
