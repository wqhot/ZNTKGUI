# -*- coding: utf-8 -*-
import cv2
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Slerp
from plotCamera import PlotCamera

class virtualCAM(object):

    def __init__(self):
        self.rot = Rotation.from_quat(np.array([0. ,0. ,0., 1.]))
        self.pos = np.array([0., 0., 0.])
        
    # 生成旋转插值 时间精度为0.01s
    def gen_rot_slerp(self, t, rot):
        rot = np.array(rot)
        if np.linalg.norm(rot) == 0:
            return None
        key_rots = np.zeros(shape=(2, 4))
        key_rots[0, :] = self.rot.as_quat()
        key_rots[1, :] = rot
        key_rots = Rotation.from_quat(key_rots)
        key_times = [0, t]
        times_slerp = np.linspace(0, t, )
        