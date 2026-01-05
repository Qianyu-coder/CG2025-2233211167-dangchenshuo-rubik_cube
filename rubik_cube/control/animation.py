# control/animation.py
import numpy as np
from typing import List, Tuple
from model.cubie import Cubie


class AnimationState:
    """单个动画帧状态"""

    def __init__(self, face: str, direction: int, duration: float = 0.5, record_history: bool = True):
        self.face = face
        self.direction = direction  # 1=顺时针, -1=逆时针
        self.duration = duration  # 动画时长（秒）
        self.progress = 0.0  # 0.0 ~ 1.0
        self.is_complete = False
        self.record_history = record_history  # 是否写入历史

    def update(self, delta_time: float):
        """每帧更新进度"""
        if not self.is_complete:
            self.progress = min(1.0, self.progress + delta_time / self.duration)
            if self.progress >= 1.0:
                self.is_complete = True

    def get_angle(self) -> float:
        """获取当前动画角度"""
        return 90.0 * self.progress


class AnimationQueue:
    """管理动画队列，与Model层协作"""

    def __init__(self, cube):
        self.cube = cube
        self.queue: List[AnimationState] = []
        self.current_animation = None
        self.affected_cubies: List[Tuple[Cubie, Tuple[int, int, int]]] = []

    def add_solution(self, moves: List[Tuple[str, int]]):
        for face, direction in moves:
            self.add_rotation(face, direction) 

    def add_rotation(self, face: str, direction: int, record_history: bool = True):
        """添加旋转到队列"""
        self.queue.append(AnimationState(face, direction, record_history=record_history))

    def update(self, delta_time: float):
        """每帧调用，更新动画状态"""
        if self.current_animation is None and self.queue:
            self.current_animation = self.queue.pop(0)
            self._prepare_affected_cubies()

        if self.current_animation:
            self.current_animation.update(delta_time)
            angle = self.current_animation.get_angle()
            self._update_animation_matrices(angle)

            if self.current_animation.is_complete:
                self._finalize_rotation()
                self.current_animation = None

    def _prepare_affected_cubies(self):
        """记录受影响的小立方体及其原始位置"""
        if not self.current_animation:
            return

        face_map = {
            'F': {'axis': 'z', 'layer': 1},
            'B': {'axis': 'z', 'layer': -1},
            'U': {'axis': 'y', 'layer': 1},
            'D': {'axis': 'y', 'layer': -1},
            'L': {'axis': 'x', 'layer': -1},
            'R': {'axis': 'x', 'layer': 1},
        }

        config = face_map[self.current_animation.face]
        axis_index = {'x': 0, 'y': 1, 'z': 2}[config['axis']]
        layer = config['layer']

        self.affected_cubies = [
            (cubie, cubie.position) for pos, cubie in self.cube.cubies.items()
            if pos[axis_index] == layer
        ]

    def _update_animation_matrices(self, angle: float):
        """根据当前角度计算动画矩阵"""
        if not self.current_animation:
            return

        face = self.current_animation.face
        direction = self.current_animation.direction
        record_history = self.current_animation.record_history

        axis_vectors = {
            'F': (0, 0, 1), 'B': (0, 0, -1),
            'U': (0, 1, 0), 'D': (0, -1, 0),
            'L': (-1, 0, 0), 'R': (1, 0, 0),
        }

        axis = axis_vectors[face]
        affected_set = {c for c, _ in self.affected_cubies}

        for cubie in self.cube.cubies.values():
            if cubie in affected_set:
                # 使用魔方中心作为旋转轴点
                cubie.animation_matrix = self._create_rotation_matrix_around_center(axis, angle * direction)
            else:
                cubie.animation_matrix = None

    def _create_rotation_matrix_around_center(self, axis: tuple, angle: float):
        """创建围绕魔方中心的旋转矩阵"""
        ax, ay, az = axis
        angle_rad = np.radians(angle)
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        t = 1 - c

        matrix = np.array([
            [ax * ax * t + c,     ax * ay * t - az * s, ax * az * t + ay * s, 0],
            [ax * ay * t + az * s, ay * ay * t + c,     ay * az * t - ax * s, 0],
            [ax * az * t - ay * s, ay * az * t + ax * s, az * az * t + c,     0],
            [0,                   0,                   0,                   1]
        ], dtype=np.float32)

        return matrix.flatten()

    def _finalize_rotation(self):
        """动画完成，同步更新模型状态"""
        if not self.current_animation:
            return

        face = self.current_animation.face
        direction = self.current_animation.direction
        record_history = self.current_animation.record_history

        # 更新模型的真实状态
        self.cube.rotate_face(face, direction, animation=False, record_history=record_history)

        # 清理动画状态
        for cubie in self.cube.cubies.values():
            cubie.animation_matrix = None

        self.affected_cubies.clear()

    def add_solution(self, solution):
        """
        添加求解步骤到动画队列
        solution: 求解步骤列表，例如 ["R", "U'", "F2", ...]
        """
        if not solution:
            print("警告：尝试添加空的解法序列")
            return

        valid_faces = {'U', 'R', 'F', 'D', 'L', 'B'}

        for move in solution:
            if not move or len(move) == 0:
                continue

            face = move[0].upper()

            # 验证面的有效性
            if face not in valid_faces:
                print(f"警告：跳过无效移动 '{move}' (无效面: {face})")
                continue

            # 解析方向
            if len(move) == 1:
                direction = 1          # F
            elif move[1] == '2':
                # F2: 两个90度
                self.add_rotation(face, 1, record_history=False)
                self.add_rotation(face, 1, record_history=False)
                continue
            elif move[1] == "'" or (len(move) >= 2 and move[-1] == "'"):
                direction = -1         # F'
            elif move[1] == '3':       # 兼容某些表示法
                direction = -1
            else:
                direction = 1

            self.add_rotation(face, direction, record_history=False)

    def add_scramble(self, scramble_sequence):
        """
        添加打乱序列到动画队列
        """
        for face, direction in scramble_sequence:
            self.add_rotation(face, direction)