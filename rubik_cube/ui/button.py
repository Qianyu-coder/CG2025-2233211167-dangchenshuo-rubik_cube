# ui/button.py
import numpy as np
from typing import Tuple, Callable, Optional
from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter
import OpenGL.GLUT as glut 


class Button:
    """2D按钮"""

    def __init__(self, x: float, y: float, width: float, height: float,
                 text: str, color: Tuple[float, float, float] = (0.4, 0.4, 0.4),
                 hover_color: Tuple[float, float, float] = (0.5, 0.5, 0.5),
                 text_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        """
        x, y: 按钮左下角坐标 (归一化坐标，0-1)
        width, height: 按钮宽高 (归一化)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = np.array(color)
        self.hover_color = np.array(hover_color)
        self.text_color = text_color
        self.is_hovered = False
        self.is_visible = True

        # 点击回调函数
        self.on_click: Optional[Callable] = None

    def contains_point(self, x: float, y: float, window_width: int, window_height: int) -> bool:
        """检查点(x,y)是否在按钮内"""
        if not self.is_visible:
            return False

        # 归一化坐标转换为像素坐标
        pixel_x = x
        pixel_y = window_height - y  # OpenGL坐标转换

        # 按钮的像素坐标范围
        button_x1 = int(self.x * window_width)
        button_y1 = int(self.y * window_height)
        button_x2 = int((self.x + self.width) * window_width)
        button_y2 = int((self.y + self.height) * window_height)

        return (button_x1 <= pixel_x <= button_x2 and
                button_y1 <= pixel_y <= button_y2)

    def draw(self, window_width: int, window_height: int):
        """绘制按钮"""
        if not self.is_visible:
            return

        # 保存当前投影矩阵
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用光照和深度测试以确保按钮在顶层显示
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 计算像素坐标
        x1 = int(self.x * window_width)
        y1 = int(self.y * window_height)
        x2 = int((self.x + self.width) * window_width)
        y2 = int((self.y + self.height) * window_height)

        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.color
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(x1, y1)
        glVertex2f(x2, y1)
        glVertex2f(x2, y2)
        glVertex2f(x1, y2)
        glEnd()

        # 绘制按钮边框
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x1, y1)
        glVertex2f(x2, y1)
        glVertex2f(x2, y2)
        glVertex2f(x1, y2)
        glEnd()

        # 恢复光照和深度测试
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        # 恢复矩阵
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # 绘制文字
        self._draw_text(window_width, window_height)

    def _draw_text(self, window_width: int, window_height: int):
        """绘制按钮文字"""
        if not self.text:
            return

        # 保存当前投影矩阵
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用光照和深度测试以确保文字在顶层显示
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 计算文字位置（居中）
        x = int((self.x + self.width / 2) * window_width)
        y = int((self.y + self.height / 2) * window_height)

        # 调整位置使文字居中
        text_width = len(self.text) * 9  # 字符宽度
        x -= text_width // 2
        y += 5  # 居中调整

        # 设置文字颜色和位置
        glColor3f(*self.text_color)
        glRasterPos2f(x, y)

        # 使用模块中的字体常量进行字符绘制
        font = glut.GLUT_BITMAP_9_BY_15
        for char in self.text:
            glutBitmapCharacter(font, ord(char))

        # 恢复光照和深度测试
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # 恢复矩阵
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def set_click_callback(self, callback: Callable):
        """设置点击回调函数"""
        self.on_click = callback

    def click(self):
        """触发按钮点击"""
        if self.on_click:
            self.on_click()
