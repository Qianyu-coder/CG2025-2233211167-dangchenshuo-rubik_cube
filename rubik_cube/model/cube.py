# model/cube.py
from typing import Dict, List, Tuple
from .cubie import Cubie
import numpy as np
import random

class RubiksCube:
    """魔方整体状态管理"""

    def __init__(self):
        # 存储所有Cubie，用坐标作为key
        self.cubies: Dict[Tuple[int, int, int], Cubie] = {}
        self.history = []        # 记录所有操作
        self._init_cubies()

    def _init_cubies(self):
        """初始化3x3x3魔方，跳过(0,0,0)中心"""
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    if x == 0 and y == 0 and z == 0:
                        continue  
                    self.cubies[(x, y, z)] = Cubie((x, y, z))

    def rotate_face(self, face: str, direction: int = 1, animation: bool = False, record_history: bool = True):
        """
        旋转一个面
        face: 'F'(前), 'B'(后), 'U'(上), 'D'(下), 'L'(左), 'R'(右)
        direction: 1=顺时针, -1=逆时针
        animation: 是否触发动画
        """
        # 先记录操作
        if record_history:
            if direction == -1:
                move = face + "'"
            elif direction == 2:
                move = face + "2"
            else:
                move = face
            self.history.append(move)
        
        # 标准魔方旋转方向定义（从外面看向魔方）
        face_map = {
            'F': {'axis': 'z', 'layer': 1, 'view_from': '+Z'},
            'B': {'axis': 'z', 'layer': -1, 'view_from': '-Z'},
            'U': {'axis': 'y', 'layer': 1, 'view_from': '+Y'},
            'D': {'axis': 'y', 'layer': -1, 'view_from': '-Y'},
            'L': {'axis': 'x', 'layer': -1, 'view_from': '-X'},
            'R': {'axis': 'x', 'layer': 1, 'view_from': '+X'},
        }

        if face not in face_map:
            raise ValueError(f"Invalid face: {face}")

        config = face_map[face]
        self._rotate_layer(config['axis'], config['layer'], direction, config['view_from'])

    def _rotate_layer(self, axis: str, layer: int, direction: int, view_from: str):
        """旋转指定层"""
        axis_index = {'x': 0, 'y': 1, 'z': 2}[axis]

        # 收集该层所有Cubie
        layer_cubies = {
            pos: cubie for pos, cubie in self.cubies.items()
            if pos[axis_index] == layer
        }

        # 更新每个Cubie的位置坐标
        old_positions = list(layer_cubies.keys())
        old_to_new = {}

        for old_pos in old_positions:
            cubie = layer_cubies[old_pos]
            new_pos = self._calculate_new_position(old_pos, axis, layer, direction, view_from)
            old_to_new[old_pos] = new_pos

            # 更新cubie的位置
            cubie.position = new_pos

            # 从字典中移除旧位置
            del self.cubies[old_pos]

            # 更新颜色朝向
            cubie.colors = self._rotate_colors(cubie.colors, axis, direction, view_from)

        # 将更新后的Cubie放回字典
        for old_pos, new_pos in old_to_new.items():
            self.cubies[new_pos] = layer_cubies[old_pos]

    def _calculate_new_position(self, pos: Tuple[int, int, int], axis: str, layer: int,
                                direction: int, view_from: str) -> Tuple[int, int, int]:
        """
        计算旋转后的新位置
        从view_from方向看，顺时针为正方向
        """
        x, y, z = pos

        # 根据观察方向调整旋转方向
        if view_from in ['-X', '-Y', '-Z']:
            # 从负轴方向看，顺时针方向相反
            effective_direction = -direction
        else:
            effective_direction = direction

        if axis == 'x':
            # X层旋转
            if effective_direction == 1:  # 顺时针
                # 对于左面(L)从-X看，对于右面(R)从+X看
                return (x, z, -y)
            else:  # 逆时针
                return (x, -z, y)

        elif axis == 'y':
            # Y层旋转
            if effective_direction == 1:  # 顺时针
                # 对于顶面(U)从+Y看，对于底面(D)从-Y看
                return (-z, y, x)
            else:  # 逆时针
                return (z, y, -x)

        else:  # axis == 'z'
            # Z层旋转
            if effective_direction == 1:  # 顺时针
                # 对于前面(F)从+Z看，对于后面(B)从-Z看
                return (y, -x, z)
            else:  # 逆时针
                return (-y, x, z)

    def _rotate_colors(self, colors: Dict[str, Tuple[float, float, float]],
                   axis: str, direction: int, view_from: str) -> Dict[str, Tuple[float, float, float]]:
        """更新颜色朝向"""
        # 面法向量映射
        face_vectors = {
            '+X': (1, 0, 0), '-X': (-1, 0, 0),
            '+Y': (0, 1, 0), '-Y': (0, -1, 0),
            '+Z': (0, 0, 1), '-Z': (0, 0, -1)
        }

        vector_to_face = {v: k for k, v in face_vectors.items()}

        # 根据 view_from 调整颜色旋转方向 
        if view_from in ['-X', '-Y', '-Z']:
            effective_direction = direction
        else:
            effective_direction = -direction

        angle = 90 if effective_direction == 1 else -90
        angle_rad = np.radians(angle)

        # 构建旋转矩阵
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        if axis == 'x':
            rot_matrix = np.array([
                [1, 0, 0],
                [0, c, -s],
                [0, s, c]
            ])
        elif axis == 'y':
            rot_matrix = np.array([
                [c, 0, s],
                [0, 1, 0],
                [-s, 0, c]
            ])
        else:  # 'z'
            rot_matrix = np.array([
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1]
            ])

        # 应用旋转到每个面的法向量
        new_colors = {}
        for face_name, color in colors.items():
            vec = np.array(face_vectors[face_name])
            new_vec = np.dot(rot_matrix, vec)
            new_vec_int = tuple(int(round(x)) for x in new_vec)
            new_face_name = vector_to_face[new_vec_int]
            new_colors[new_face_name] = color

        return new_colors

    def get_cubies(self) -> List[Cubie]:
        """供View层获取渲染数据"""
        return list(self.cubies.values())

    def print_state(self):
        """打印魔方状态"""
        for (x, y, z), cubie in sorted(self.cubies.items()):
            print(f"({x},{y},{z}): {cubie.colors.keys()}")


    def apply_moves(self, moves):
        """
        应用一系列移动到魔方
        moves: 移动序列
        """
        for move in moves:
            face = move[0]
            if len(move) > 1 and move[1] == "'":
                direction = -1
            elif len(move) > 1 and move[1] == '2':
                # 180度转动能分解为两次90度转动
                self.rotate_face(face, 1)
                self.rotate_face(face, 1)
                continue
            else:
                direction = 1
            self.rotate_face(face, direction)

    def scramble(self, moves=20):
        """
        随机打乱魔方
        moves: 打乱步数
        """
        faces = ['F', 'B', 'U', 'D', 'L', 'R']
        directions = [1, -1]

        scramble_sequence = []
        last_face = None

        for _ in range(moves):
            # 避免连续操作同一面
            face = random.choice(faces)
            while face == last_face:
                face = random.choice(faces)

            direction = random.choice(directions)
            scramble_sequence.append((face, direction))
            last_face = face

        # 不要在这里直接应用旋转，只返回序列
        return scramble_sequence

    def reset_to_solved_state(self):
        """
        重置为已解决状态
        """
        self.cubies.clear()
        self._init_cubies()

    def get_solution_by_reversal(self) -> List[str]:
        """返回倒序逆操作"""
        solution = []
        for move in reversed(self.history):
            if move.endswith("'"):
                # R' → R
                solution.append(move[0])
            elif move.endswith("2"):
                # R2 → R2
                solution.append(move)
            else:
                # R → R'
                solution.append(move + "'")
        return solution

    def clear_history(self):
        self.history.clear()

