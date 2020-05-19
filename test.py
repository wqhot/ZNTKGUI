# -*- coding: utf-8 -*-
"""
Demonstrate use of GLLinePlotItem to draw cross-sections of a surface.

"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 40
w.show()
w.setWindowTitle('pyqtgraph example: GLLinePlotItem')

gx = gl.GLGridItem()
gx.rotate(90, 0, 1, 0)
gx.translate(-10, 0, 0)
w.addItem(gx)
gy = gl.GLGridItem()
gy.rotate(90, 1, 0, 0)
gy.translate(0, -10, 0)
w.addItem(gy)
gz = gl.GLGridItem()
gz.translate(0, 0, -10)
w.addItem(gz)

imlt = [-1.0, -0.5, 1.0]
imrt = [1.0, -0.5, 1.0]
imlb = [-1.0,  0.5, 1.0]
imrb = [1.0,  0.5, 1.0]
lt0 = [-0.7, -0.5, 1.0]
lt1 = [-0.7, -0.2, 1.0]
lt2 = [-1.0, -0.2, 1.0]
oc = [0.0, 0.0, 0.0]

def drawLine(start, end):
    x = np.linspace(start[0], end[0], 50)
    y = np.linspace(start[1], end[1], 50)
    z = np.linspace(start[2], end[2], 50)
    pts = np.vstack([x,y,z]).transpose()
    plt = gl.GLLinePlotItem(pos=pts, antialias=True)
    w.addItem(plt)

def quaternion_to_rotation_matrix(quat):
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


def add_pose(p, q):
    rot_matrix = quaternion_to_rotation_matrix(q)
    pt_lt = np.matmul(rot_matrix, imlt) + p
    pt_lb = np.matmul(rot_matrix, imlb) + p
    pt_rt = np.matmul(rot_matrix, imrt) + p
    pt_rb = np.matmul(rot_matrix, imrb) + p
    pt_lt0 = rot_matrix * lt0
    pt_lt1 = rot_matrix * lt1
    pt_lt2 = rot_matrix * lt2
    pt_oc = np.matmul(rot_matrix, oc) + p
    drawLine(pt_lt, pt_rt)
    drawLine(pt_lt, pt_lb)
    drawLine(pt_lb, pt_rb)
    drawLine(pt_rb, pt_rt)
    drawLine(pt_oc, pt_lt)
    drawLine(pt_oc, pt_lb)
    drawLine(pt_oc, pt_rb)
    drawLine(pt_oc, pt_rt)

add_pose([0, 0, 0], [-0.460,  -0.003,  -0.842,   0.281])

add_pose([100, 0, 0], [1.0,  0.0, 0.0,   0.0])

# def fn(x, y):
#     return np.cos((x**2 + y**2)**0.5)

# n = 51
# y = np.linspace(-10,10,n)
# x = np.linspace(-10,10,100)
# for i in range(n):
#     yi = np.array([y[i]]*100)
#     d = (x**2 + yi**2)**0.5
#     z = 10 * np.cos(d) / (d+1)
#     pts = np.vstack([x,yi,z]).transpose()
#     plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
#     w.addItem(plt)
    


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
