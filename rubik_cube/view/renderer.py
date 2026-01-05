# view/renderer.py
from OpenGL.GL import *
from .camera import Camera
from .interfaces import ICubie
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


class Renderer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.camera = Camera()
        self._is_gl_initialized = False
        self.input_handler = None
        self.ui_manager = None  # 新增UI管理器引用

        # 魔方整体缩放比例
        self.cube_scale = 1.0
        self.target_scale = 1.0
        self.min_scale = 0.3
        self.max_scale = 3.0

    def bind_input_handler(self, input_handler):
        """绑定输入处理器以获取魔方旋转状态"""
        self.input_handler = input_handler

    def bind_ui_manager(self, ui_manager):
        """绑定UI管理器"""
        self.ui_manager = ui_manager

    def initialize_gl(self):
        """在glutCreateWindow()后调用"""
        if self._is_gl_initialized:
            return

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        # 光照设置
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 1.5, 1.5, 1.0])

        # 设置材质
        material_ambient = [0.2, 0.2, 0.2, 1.0]
        material_diffuse = [0.5, 0.5, 0.5, 1.0]
        material_specular = [1.0, 1.0, 1.0, 1.0]
        material_shininess = [30.0]

        glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

        self._is_gl_initialized = True

    def get_modelview_matrix(self):
        """获取当前模型视图矩阵"""
        return glGetDoublev(GL_MODELVIEW_MATRIX)

    def get_projection_matrix(self):
        """获取当前投影矩阵"""
        return glGetDoublev(GL_PROJECTION_MATRIX)

    def begin_frame(self):
        """每帧渲染前调用"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.width, self.height)

        # 设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width / self.height, 0.1, 100)

        # 设置视图矩阵
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 应用相机视角
        self.camera.apply_view_matrix()

        # 新增：应用魔方旋转
        if self.input_handler:
            rotation = self.input_handler.get_cube_rotation()
            glRotatef(rotation['x'], 1, 0, 0)
            glRotatef(rotation['y'], 0, 1, 0)

        current_scale = self.cube_scale + (self.target_scale - self.cube_scale) * 0.15
        self.cube_scale = current_scale
        glScalef(current_scale, current_scale, current_scale)
        glEnable(GL_NORMALIZE)

    def end_frame(self):
        """每帧渲染后调用 - 新增UI绘制"""
        # 在绘制UI之前禁用深度测试，确保UI显示在最前面
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 绘制UI（使用2D正交投影）
        if self.ui_manager and self.ui_manager.is_visible:
            self.ui_manager.draw()

        # 恢复设置
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

    def render(self, mock_cubies):
        """主渲染入口"""
        self.begin_frame()

        # 遍历绘制每个Cubie
        for cubie in mock_cubies:
            self.draw_cubie(cubie)

        self.end_frame()

    def draw_cubie(self, cubie: ICubie):
        glPushMatrix()

        pos = cubie.get_position()
        matrix = cubie.get_animation_matrix()

        if matrix is not None:
            glMultMatrixf(matrix)
            glTranslatef(*[p * 1.15 for p in pos])
        else:
            glTranslatef(*[p * 1.15 for p in pos])

        # 绘制面
        self._draw_cubie_faces(cubie.get_colors(), cubie.get_position())

        glPopMatrix()

    def _draw_cubie_faces(self, colors: dict, position: tuple):
        """绘制Cubie的6个面，内部面使用深银灰色金属质感"""
        face_size = 0.5

        faces = [
            ((0, 0, 1), [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)], '+Z'),
            ((0, 0, -1), [(-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)], '-Z'),
            ((1, 0, 0), [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)], '+X'),
            ((-1, 0, 0), [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)], '-X'),
            ((0, 1, 0), [(-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)], '+Y'),
            ((0, -1, 0), [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)], '-Y'),
        ]

        glBegin(GL_QUADS)
        for normal, vertices, face_key in faces:
            if self._is_internal_face(position, face_key):
                # 内部面使用深银灰色金属质感（比之前更暗一点）
                dark_silver_color = (0.4, 0.4, 0.4)  # 深银灰色
                glColor3f(*dark_silver_color)
            else:
                # 外表面使用光影效果
                base_color = colors.get(face_key, (0.2, 0.2, 0.2))
                light_factor = 1.0
                if face_key in ['+Y']:
                    light_factor = 1.1
                elif face_key in ['-Y']:
                    light_factor = 0.9
                elif face_key in ['+Z', '+X']:
                    light_factor = 1.05
                elif face_key in ['-Z', '-X']:
                    light_factor = 0.95

                adjusted_color = tuple(min(1.0, c * light_factor) for c in base_color)
                glColor3f(*adjusted_color)

            glNormal3f(*normal)

            for vertex in vertices:
                glVertex3f(*[v * face_size for v in vertex])

        glEnd()

    def _is_internal_face(self, position, face_key):
        """判断是否为不可见的内部面"""
        x, y, z = position

        if face_key == '+X' and x != 1:
            return True
        elif face_key == '-X' and x != -1:
            return True
        elif face_key == '+Y' and y != 1:
            return True
        elif face_key == '-Y' and y != -1:
            return True
        elif face_key == '+Z' and z != 1:
            return True
        elif face_key == '-Z' and z != -1:
            return True

        return False
