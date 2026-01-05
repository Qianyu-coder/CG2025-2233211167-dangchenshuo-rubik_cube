# view/camera.py
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    def __init__(self):
        self.distance = 8.0  # 相机距离
        self.pitch = -30.0  # 上下角度
        self.yaw = 45.0  # 左右角度
        self.is_dragging = False
        self.last_mouse = (0, 0)

    def apply_view_matrix(self):
        """在渲染前调用，设置观察矩阵"""
        glLoadIdentity()
        # 计算相机位置
        eye_x = self.distance * np.cos(np.radians(self.pitch)) * np.cos(np.radians(self.yaw))
        eye_y = self.distance * np.sin(np.radians(self.pitch))
        eye_z = self.distance * np.cos(np.radians(self.pitch)) * np.sin(np.radians(self.yaw))

        gluLookAt(eye_x, eye_y, eye_z, 0, 0, 0, 0, 1, 0)

    def handle_mouse_down(self, x, y):
        self.is_dragging = True
        self.last_mouse = (x, y)

    def handle_mouse_drag(self, x, y):
        if not self.is_dragging:
            return
        dx = x - self.last_mouse[0]
        dy = y - self.last_mouse[1]

        self.yaw += dx * 0.3
        self.pitch = max(-89, min(89, self.pitch - dy * 0.3))

        self.last_mouse = (x, y)

    def handle_mouse_up(self):
        self.is_dragging = False