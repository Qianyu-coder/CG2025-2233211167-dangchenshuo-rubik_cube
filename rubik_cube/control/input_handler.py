# control/input_handler.py
import time
from OpenGL.GLUT import *
from model.cube import RubiksCube
from control.animation import AnimationQueue
import numpy as np
from OpenGL.GLU import gluUnProject
from control.solver_controller import SolverController

class InputHandler:
    def __init__(self, cube: RubiksCube, animation_queue: AnimationQueue):
        self.cube = cube
        self.animation_queue = animation_queue

        # 鼠标状态
        self.is_dragging = False
        self.last_mouse = (0, 0)

        # 相机实例
        self.camera = None

        # 魔方旋转状态
        self.cube_rotation = {
            'x': 0.0,
            'y': 0.0,
            'dragging': False,
            'last_x': 0,
            'last_y': 0
        }

        # 渲染器引用
        self.renderer = None

        # UI管理器引用
        self.ui_manager = None

        # 鼠标点击跟踪
        self.mouse_down_pos = (0, 0)
        self.mouse_down_time = 0
        self.click_threshold = 0.2

        # 求解控制器引用
        self.solver_controller = None 

    def scroll(self, wheel, direction, x, y):
        """鼠标滚轮回调"""
        if not self.animation_queue.current_animation:
            delta = 0.15 if direction > 0 else -0.15
            if self.renderer:
                self.renderer.target_scale = np.clip(
                    self.renderer.target_scale + delta,
                    self.renderer.min_scale,
                    self.renderer.max_scale
                )
                glutPostRedisplay()

    def bind_camera(self, camera):
        """绑定相机"""
        self.camera = camera

    def bind_renderer(self, renderer):
        """绑定渲染器以获取矩阵信息"""
        self.renderer = renderer

    def bind_ui_manager(self, ui_manager):
        """绑定UI管理器"""
        self.ui_manager = ui_manager
        # 设置按钮回调
        self._setup_button_callbacks()

    def bind_solver_controller(self, solver_controller: SolverController):
        """绑定求解控制器"""
        self.solver_controller = solver_controller

    def _setup_button_callbacks(self):
        """设置按钮回调函数"""
        if not self.ui_manager:
            return

        # 打乱按钮回调
        self.ui_manager.bind_scramble_callback(self._on_scramble_button_click)

        # 快速打乱按钮回调
        self.ui_manager.bind_quick_scramble_callback(self._on_quick_scramble_button_click)

        # 重置按钮回调
        self.ui_manager.bind_reset_callback(self._on_reset_button_click)

        # 求解按钮回调
        self.ui_manager.bind_solve_callback(self._on_solve_button_click)

        # 使用说明按钮回调
        self.ui_manager.bind_instructions_callback(self._on_instructions_clicked)


    def _on_scramble_button_click(self):
        """打乱按钮点击回调"""
        if not self.animation_queue.current_animation:
            # 保留历史
            scramble_seq = self.cube.scramble(20)
            self.animation_queue.add_scramble(scramble_seq)
            glutPostRedisplay()
            print("开始打乱魔方...")

    def _on_quick_scramble_button_click(self):
        """快速打乱按钮点击回调"""
        if not self.animation_queue.current_animation:
            # 保留历史
            self.animation_queue.queue.clear()
            if self.animation_queue.current_animation:
                self.animation_queue.current_animation = None

            # 生成并直接应用打乱序列
            scramble_seq = self.cube.scramble(20)
            for face, direction in scramble_seq:
                self.cube.rotate_face(face, direction)
            glutPostRedisplay()
            print("魔方已快速打乱")

    def _on_reset_button_click(self):
        """重置按钮点击回调 - 高优先级"""
        # 立即清除所有动画
        self.animation_queue.queue.clear()
        self.animation_queue.current_animation = None

        # 重置魔方状态
        self.cube.reset_to_solved_state()
        self.cube.clear_history() 
        glutPostRedisplay()
        print("魔方已重置")

    def _on_solve_button_click(self):
        """求解按钮回调：使用两阶段算法求解"""
        if self.solver_controller and not self.animation_queue.current_animation:
            print("开始使用两阶段算法求解魔方...")
            solution = self.solver_controller.solve_cube()
            if solution:
                self.cube.clear_history() 
                print(f"求解完成，共 {len(solution)} 步")
            else:
                print("求解失败或未找到解法")

    def keyboard(self, key: bytes, x: int, y: int):
        """键盘事件：字母键 = 顺时针，Shift+字母 = 逆时针"""
        # 处理高优先级的重置操作
        if key == b'c' or key == b'C':
            self._on_reset_button_click()
            return

        # 其他操作只有在没有动画时才能执行
        if not self.animation_queue.current_animation:
            mapping = {
                b'g': ('F', 1), b'G': ('F', -1),
                b'b': ('B', 1), b'B': ('B', -1),
                b'r': ('U', 1), b'R': ('U', -1),
                b'o': ('D', 1), b'O': ('D', -1),
                b'w': ('L', 1), b'W': ('L', -1),
                b'y': ('R', 1), b'Y': ('R', -1),
                # 打乱功能
                b's': ('SCRAMBLE', 1),
                b'S': ('SCRAMBLE_INSTANT', 1),
                # UI可见性切换
                b'u': ('TOGGLE_UI', 1),  # 按U键切换UI显示
                # Enter键触发回溯算法求解
                b'\r': ('SOLVE_TWO_PHASE', 1),
                b'\b': ('SOLVE', 1),
            }

            if key in mapping:
                action, direction = mapping[key]

                if action == 'SCRAMBLE':
                    self._on_scramble_button_click()
                elif action == 'SCRAMBLE_INSTANT':
                    scramble_seq = self.cube.scramble(20)
                    for face, direction in scramble_seq:
                        self.cube.rotate_face(face, direction)
                    glutPostRedisplay()
                    print("魔方已打乱")
                elif action == 'TOGGLE_UI':
                    if self.ui_manager:
                        self.ui_manager.toggle_visibility()
                        glutPostRedisplay()
                        print(f"UI显示: {'开' if self.ui_manager.is_visible else '关'}")
                elif action == 'SOLVE_TWO_PHASE':
                    # 使用两阶段算法求解
                    if self.solver_controller and not self.animation_queue.current_animation:
                        print("开始使用两阶段算法求解魔方...")
                        solution = self.solver_controller.solve_cube()
                        if solution:
                            self.cube.clear_history() 
                            print(f"求解完成，共 {len(solution)} 步")
                        else:
                            print("求解失败或未找到解法")
                elif action == 'SOLVE':
                    self._on_undo_all_button_click()          # 回溯法求解
                else:
                    self.animation_queue.add_rotation(action, direction)
                    glutPostRedisplay()

    def special_keyboard(self, key: int, x: int, y: int):
        """特殊键（方向键等）"""
        pass

    def mouse(self, button: int, state: int, x: int, y: int) -> bool:
        """
        鼠标点击事件
        返回True表示事件已被处理，False表示未处理（用于UI）
        """
        # 检查说明面板点击
        if state == GLUT_DOWN and self.ui_manager and self.ui_manager.is_visible:
            if self.ui_manager.handle_instructions_click(x, y):
                glutPostRedisplay()
                return True

        # 检查UI点击 - 使用当前窗口尺寸
        if state == GLUT_DOWN and self.ui_manager and self.ui_manager.is_visible:
            if self.ui_manager.handle_mouse_click(x, y):
                glutPostRedisplay()
                return True 

        if state == GLUT_DOWN:
            self.mouse_down_pos = (x, y)
            self.mouse_down_time = time.time()

            if button == GLUT_LEFT_BUTTON:
                self.is_dragging = True
                self.last_mouse = (x, y)
                self.cube_rotation['dragging'] = True
                self.cube_rotation['last_x'] = x
                self.cube_rotation['last_y'] = y
                if self.camera:
                    self.camera.handle_mouse_down(x, y)
        elif state == GLUT_UP:
            if button == GLUT_LEFT_BUTTON:
                hold_duration = time.time() - self.mouse_down_time

                if hold_duration < self.click_threshold and not self.animation_queue.current_animation:
                    clicked_face = self._get_clicked_face(x, y)
                    if clicked_face:
                        self.animation_queue.add_rotation(clicked_face, 1)
                        glutPostRedisplay()

                self.is_dragging = False
                self.cube_rotation['dragging'] = False
                if self.camera:
                    self.camera.handle_mouse_up()
            elif button == GLUT_RIGHT_BUTTON and not self.animation_queue.current_animation:
                hold_duration = time.time() - self.mouse_down_time
                if hold_duration < self.click_threshold:
                    clicked_face = self._get_clicked_face(x, y)
                    if clicked_face:
                        self.animation_queue.add_rotation(clicked_face, -1)
                        glutPostRedisplay()

        return False

    def motion(self, x: int, y: int):
        """鼠标拖拽事件"""
        # 更新UI悬停状态
        if self.ui_manager and self.ui_manager.is_visible:
            self.ui_manager.handle_mouse_move(x, y)

        # 处理魔方旋转
        if self.cube_rotation['dragging']:
            delta_x = x - self.cube_rotation['last_x']
            delta_y = y - self.cube_rotation['last_y']

            self.cube_rotation['x'] += delta_y * 0.5
            self.cube_rotation['y'] += delta_x * 0.5

            self.cube_rotation['last_x'] = x
            self.cube_rotation['last_y'] = y

            glutPostRedisplay()
        # 保留原有的相机控制
        elif self.is_dragging and self.camera:
            dx = x - self.last_mouse[0]
            dy = y - self.last_mouse[1]

            self.camera.handle_mouse_drag(x, y)
            self.last_mouse = (x, y)
            glutPostRedisplay()

    def get_cube_rotation(self):
        """获取魔方旋转状态，供渲染器使用"""
        return self.cube_rotation

    def _get_clicked_face(self, x, y):
        """根据鼠标坐标确定点击的魔方面"""
        if not self.renderer:
            return None

        # 使用当前窗口的实际尺寸而不是硬编码的800x600
        viewport = [0, 0, self.renderer.width, self.renderer.height]
        modelview = self.renderer.get_modelview_matrix()
        projection = self.renderer.get_projection_matrix()

        ray_origin, ray_direction = self._unproject_ray(x, y, viewport, modelview, projection)

        face_definitions = {
            'F': {
                'center': np.array([0, 0, 1.65]),
                'normal': np.array([0, 0, 1]),
                'vertices': [
                    np.array([-1.65, -1.65, 1.65]),
                    np.array([1.65, -1.65, 1.65]),
                    np.array([1.65, 1.65, 1.65]),
                    np.array([-1.65, 1.65, 1.65])
                ]
            },
            'B': {
                'center': np.array([0, 0, -1.65]),
                'normal': np.array([0, 0, -1]),
                'vertices': [
                    np.array([1.65, -1.65, -1.65]),
                    np.array([-1.65, -1.65, -1.65]),
                    np.array([-1.65, 1.65, -1.65]),
                    np.array([1.65, 1.65, -1.65])
                ]
            },
            'R': {
                'center': np.array([1.65, 0, 0]),
                'normal': np.array([1, 0, 0]),
                'vertices': [
                    np.array([1.65, -1.65, -1.65]),
                    np.array([1.65, -1.65, 1.65]),
                    np.array([1.65, 1.65, 1.65]),
                    np.array([1.65, 1.65, -1.65])
                ]
            },
            'L': {
                'center': np.array([-1.65, 0, 0]),
                'normal': np.array([-1, 0, 0]),
                'vertices': [
                    np.array([-1.65, -1.65, 1.65]),
                    np.array([-1.65, -1.65, -1.65]),
                    np.array([-1.65, 1.65, -1.65]),
                    np.array([-1.65, 1.65, 1.65])
                ]
            },
            'U': {
                'center': np.array([0, 1.65, 0]),
                'normal': np.array([0, 1, 0]),
                'vertices': [
                    np.array([-1.65, 1.65, 1.65]),
                    np.array([1.65, 1.65, 1.65]),
                    np.array([1.65, 1.65, -1.65]),
                    np.array([-1.65, 1.65, -1.65])
                ]
            },
            'D': {
                'center': np.array([0, -1.65, 0]),
                'normal': np.array([0, -1, 0]),
                'vertices': [
                    np.array([-1.65, -1.65, -1.65]),
                    np.array([1.65, -1.65, -1.65]),
                    np.array([1.65, -1.65, 1.65]),
                    np.array([-1.65, -1.65, 1.65])
                ]
            }
        }

        camera_pos = self._extract_camera_position(modelview)

        valid_faces = []
        face_distances = {}

        for face_name, face_data in face_definitions.items():
            center = face_data['center']
            normal = face_data['normal']
            vertices = face_data['vertices']

            to_camera = camera_pos - center
            to_camera = to_camera / np.linalg.norm(to_camera)

            if np.dot(normal, to_camera) > 0:
                result = self._intersect_ray_with_quad(ray_origin, ray_direction, vertices, normal, center)
                if result:
                    t, intersection = result
                    if t >= 0:
                        valid_faces.append(face_name)
                        face_distances[face_name] = t

        if valid_faces:
            closest_face = min(valid_faces, key=lambda f: face_distances[f])
            return closest_face

        return None

    def _extract_camera_position(self, modelview_matrix):
        """从模型视图矩阵中提取相机位置"""
        try:
            inv_matrix = np.linalg.inv(modelview_matrix)
            camera_pos = np.array([inv_matrix[3, 0], inv_matrix[3, 1], inv_matrix[3, 2]])
            return camera_pos
        except np.linalg.LinAlgError:
            return np.array([0, 0, 8])

    def _unproject_ray(self, x, y, viewport, modelview, projection):
        """将屏幕坐标转换为3D射线"""
        near_point = gluUnProject(x, viewport[3] - y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(x, viewport[3] - y, 1.0, modelview, projection, viewport)

        ray_origin = np.array(near_point)
        ray_direction = np.array(far_point) - ray_origin
        ray_direction = ray_direction / np.linalg.norm(ray_direction)

        return ray_origin, ray_direction

    def _intersect_ray_with_quad(self, ray_origin, ray_direction, vertices, normal, center):
        """检测射线与四边形面的交点"""
        denom = np.dot(ray_direction, normal)
        if abs(denom) < 1e-6:
            return None

        t = np.dot(center - ray_origin, normal) / denom
        if t < 0:
            return None

        intersection = ray_origin + t * ray_direction

        if self._point_in_quad(intersection, vertices):
            return t, intersection

        return None

    def _point_in_quad(self, point, vertices):
        """使用叉积法检查点是否在四边形内"""
        tolerance = 1e-3

        n_vertices = len(vertices)
        for i in range(n_vertices):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n_vertices]

            edge = v2 - v1
            to_point = point - v1

            cross = np.cross(edge, to_point)

            face_normal = np.cross(edge, vertices[(i + 2) % n_vertices] - v2)

            if np.linalg.norm(face_normal) > 1e-6:
                face_normal = face_normal / np.linalg.norm(face_normal)

            if np.dot(cross, face_normal) < -tolerance:
                return False

        return True

    def _on_instructions_clicked(self):
        """使用说明按钮点击回调"""
        if self.ui_manager:
            self.ui_manager.toggle_instructions_visibility()
            glutPostRedisplay()
            print(f"使用说明面板: {'显示' if self.ui_manager.instructions_visible else '隐藏'}")

    def _on_undo_all_button_click(self):
        """复原：倒放打乱动画"""
        if self.animation_queue.current_animation:
            print("请等待当前动画结束")
            return
        if not self.cube.history:
            print("没有打乱记录，无法复原")
            return

        print(f"正在倒放复原（{len(self.cube.history)} 步）...")
        solution = self.cube.get_solution_by_reversal()
        self.animation_queue.add_solution(solution)
        # 复原后清空历史
        self.cube.clear_history()
        glutPostRedisplay()
    


