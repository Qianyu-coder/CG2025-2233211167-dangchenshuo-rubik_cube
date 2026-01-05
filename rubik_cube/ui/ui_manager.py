# ui/ui_manager.py
from typing import List, Optional
from .button import Button
from OpenGL.GL import (
    glPushAttrib, glPopAttrib, GL_ALL_ATTRIB_BITS,
    glMatrixMode, glPushMatrix, glLoadIdentity, glOrtho, glPopMatrix,  # 添加 glPopMatrix
    GL_PROJECTION, GL_MODELVIEW,
    glDisable, glEnable, GL_DEPTH_TEST, GL_LIGHTING, GL_BLEND,
    glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    glColor4f, glBegin, glEnd, GL_QUADS, GL_LINE_LOOP, GL_LINES,
    glVertex2f, glLineWidth, glColor3f,
    glRasterPos2f
)


# 单独从GLUT模块导入glutBitmapCharacter
from OpenGL.GLUT import glutBitmapCharacter

import OpenGL.GLUT as glut

class UIManager:
    """管理UI元素的类"""

    def __init__(self, window_width: int = 800, window_height: int = 600):
        self.window_width = window_width
        self.window_height = window_height
        self.buttons: List[Button] = []
        self.is_visible = True
        self.show_instructions = False  # 控制说明面板显示状态
        self.solver_controller = None  # 求解控制器引用


        # 回调函数
        self.scramble_callback = None
        self.quick_scramble_callback = None
        self.reset_callback = None
        self.solve_callback = None
        self.instructions_callback = None  # 说明回调

        # 创建默认UI元素
        self._create_default_elements()

    def bind_solver_controller(self, solver_controller):
        """绑定求解控制器"""
        self.solver_controller = solver_controller
        # 绑定求解按钮回调
        for button in self.buttons:
            if button.text.startswith("Solve"):
                button.set_click_callback(self._on_solve_clicked)

    def _create_default_elements(self):
        """创建默认的UI元素"""
        self._create_default_buttons()

    def _create_default_buttons(self):
        """创建默认的控制按钮"""
        # 打乱按钮（带动画）
        scramble_btn = Button(
            x=0.02, y=0.85, width=0.18, height=0.08,
            text="Scramble",
            color=(0.2, 0.6, 0.2),  
            hover_color=(0.3, 0.7, 0.3),
            text_color=(1.0, 1.0, 1.0)
        )

        # 快速打乱按钮（无动画）
        quick_scramble_btn = Button(
            x=0.02, y=0.75, width=0.18, height=0.08,
            text="Q-Scramble (S)",
            color=(0.6, 0.6, 0.2), 
            hover_color=(0.7, 0.7, 0.3),
            text_color=(1.0, 1.0, 1.0)
        )

        # 重置按钮
        reset_btn = Button(
            x=0.02, y=0.65, width=0.18, height=0.08,
            text="Reset (C)",
            color=(0.6, 0.2, 0.2), 
            hover_color=(0.7, 0.3, 0.3),
            text_color=(1.0, 1.0, 1.0)
        )

        # 求解按钮
        solve_btn = Button(
            x=0.02, y=0.55, width=0.18, height=0.08,
            text="Solve",
            color=(0.2, 0.4, 0.6),  # 蓝色
            hover_color=(0.3, 0.5, 0.7),
            text_color=(1.0, 1.0, 1.0)
        )

        # 使用说明按钮
        instructions_btn = Button(
            x=0.02, y=0.45, width=0.18, height=0.08,
            text="Instructions",
            color=(0.2, 0.2, 0.6),  # 蓝色
            hover_color=(0.3, 0.3, 0.7),
            text_color=(1.0, 1.0, 1.0)
        )

        self.buttons.extend([scramble_btn, quick_scramble_btn, reset_btn, solve_btn, instructions_btn])

    def handle_mouse_move(self, x: int, y: int):
        """处理鼠标移动，更新按钮悬停状态"""
        if not self.is_visible:
            return

        for button in self.buttons:
            if button.is_visible:
                button.is_hovered = button.contains_point(x, y, self.window_width, self.window_height)

    def handle_mouse_click(self, x: int, y: int) -> bool:
        """处理鼠标点击，返回True表示点击了UI元素"""
        if not self.is_visible:
            return False

        for button in self.buttons:
            if button.is_visible and button.contains_point(x, y, self.window_width, self.window_height):
                button.click()
                return True
        return False

    def draw(self):
        """绘制所有UI元素"""
        if not self.is_visible:
            return

        # 绘制按钮
        for button in self.buttons:
            button.draw(self.window_width, self.window_height)

        # 绘制使用说明面板
        if self.show_instructions:
            self._draw_instructions_panel()

    def _draw_instructions_panel(self):
        """绘制使用说明面板"""
        # 保存当前OpenGL状态
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        # 设置2D正交投影
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.window_width, 0, self.window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用光照和深度测试以确保UI在顶层显示
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 计算面板位置和大小
        panel_width = 500
        panel_height = 500
        panel_x = (self.window_width - panel_width) // 2
        panel_y = (self.window_height - panel_height) // 2

        # 绘制半透明背景
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.1, 0.1, 0.85) 
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()
        glDisable(GL_BLEND)

        # 绘制面板边框
        glColor3f(0.8, 0.8, 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()

        # 绘制标题
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(panel_x + 20, panel_y + panel_height - 30)
        title = "instructions"
        font = glut.GLUT_BITMAP_HELVETICA_18
        for char in title:
            glutBitmapCharacter(font, ord(char))

        # 绘制关闭按钮
        close_btn_size = 20
        close_btn_x = panel_x + panel_width - close_btn_size - 10
        close_btn_y = panel_y + panel_height - close_btn_size - 10

        # 关闭按钮背景
        glColor3f(0.8, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(close_btn_x, close_btn_y)
        glVertex2f(close_btn_x + close_btn_size, close_btn_y)
        glVertex2f(close_btn_x + close_btn_size, close_btn_y + close_btn_size)
        glVertex2f(close_btn_x, close_btn_y + close_btn_size)
        glEnd()

        # 关闭按钮"X"
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(close_btn_x + 5, close_btn_y + 5)
        glVertex2f(close_btn_x + close_btn_size - 5, close_btn_y + close_btn_size - 5)
        glVertex2f(close_btn_x + close_btn_size - 5, close_btn_y + 5)
        glVertex2f(close_btn_x + 5, close_btn_y + close_btn_size - 5)
        glEnd()

        # 绘制说明内容
        instructions = [
            "Key Controls:",
            "• s: Random scramble 20 (animated)",
            "• S: Instant scramble 20",
            "• c: Reset to solved",
            "• Enter: Solve using TwoPhaseSolver",
            "• Backspace: Solve using backtracking",
            "",
            "Mouse Controls:",
            "• Left-click face: Rotate face clockwise 90°",
            "• Right-click face: Rotate face counterclockwise 90°",
            "• Scroll wheel: Zoom in/out",
            "• Drag with left button: Rotate view angle",
            "",
            "UI Buttons:",
            "• Scramble: Animate 20 random moves",
            "• Q-Scramble: Instant 20 random moves (S)",
            "• Reset: Back to solved state (C)",
            "• Solve: Solve with animation",
            "• Instructions: Toggle this panel",
        ]

        font = glut.GLUT_BITMAP_9_BY_15
        line_height = 20
        start_y = panel_y + panel_height - 70

        glColor3f(1.0, 1.0, 1.0)
        for i, line in enumerate(instructions):
            glRasterPos2f(panel_x + 20, start_y - i * line_height)
            for char in line:
                glutBitmapCharacter(font, ord(char))

        # 恢复OpenGL状态
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def handle_instructions_click(self, x: int, y: int) -> bool:
        """处理说明面板的点击事件"""
        if not self.show_instructions:
            return False

        # 计算面板位置和大小
        panel_width = 500
        panel_height = 500
        panel_x = (self.window_width - panel_width) // 2
        panel_y = (self.window_height - panel_height) // 2

        # 转换Y坐标系
        converted_y = self.window_height - y

        # 检查是否点击了关闭按钮
        close_btn_size = 20
        close_btn_x = panel_x + panel_width - close_btn_size - 10
        close_btn_y = panel_y + panel_height - close_btn_size - 10

        if (close_btn_x <= x <= close_btn_x + close_btn_size and
                close_btn_y <= converted_y <= close_btn_y + close_btn_size):
            self.show_instructions = False
            return True

        # 检查是否点击了面板区域
        if (panel_x <= x <= panel_x + panel_width and
                panel_y <= converted_y <= panel_y + panel_height):
            return True

        return False

    def resize(self, width: int, height: int):
        """窗口大小改变时调用"""
        self.window_width = width
        self.window_height = height

    def _on_scramble_clicked(self):
        """打乱按钮点击处理"""
        if self.scramble_callback:
            self.scramble_callback()

    def _on_quick_scramble_clicked(self):
        """快速打乱按钮点击处理"""
        if self.quick_scramble_callback:
            self.quick_scramble_callback()

    def _on_reset_clicked(self):
        """重置按钮点击处理"""
        if self.reset_callback:
            self.reset_callback()

    def _on_instructions_clicked(self):
        """使用说明按钮点击处理"""
        self.show_instructions = not self.show_instructions

    def bind_scramble_callback(self, callback):
        """绑定打乱按钮回调"""
        self.scramble_callback = callback
        for button in self.buttons:
            if button.text == "Scramble":
                button.set_click_callback(self._on_scramble_clicked)

    def bind_quick_scramble_callback(self, callback):
        """绑定快速打乱按钮回调"""
        self.quick_scramble_callback = callback
        for button in self.buttons:
            if button.text.startswith("Q-Scramble"):
                button.set_click_callback(self._on_quick_scramble_clicked)

    def bind_reset_callback(self, callback):
        """绑定重置按钮回调"""
        self.reset_callback = callback
        for button in self.buttons:
            if button.text.startswith("Reset"):
                button.set_click_callback(self._on_reset_clicked)

    def bind_instructions_callback(self, callback):
        """绑定使用说明按钮回调"""
        self.instructions_callback = callback
        for button in self.buttons:
            if button.text == "Instructions":
                button.set_click_callback(self._on_instructions_clicked)

    def toggle_visibility(self):
        """切换UI可见性"""
        self.is_visible = not self.is_visible

    def _on_solve_clicked(self):
        """求解按钮点击处理"""
        if self.solver_controller:
            self.solver_controller.solve_cube()
        elif self.solve_callback:
            self.solve_callback()

    def bind_solve_callback(self, callback):
        """绑定求解按钮回调"""
        self.solve_callback = callback
        for button in self.buttons:
            if button.text.startswith("Solve"):
                button.set_click_callback(self._on_solve_clicked)


