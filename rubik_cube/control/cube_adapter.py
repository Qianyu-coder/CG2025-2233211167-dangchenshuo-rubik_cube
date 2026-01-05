# control/cube_adapter.py
from model.cube import RubiksCube
from typing import Dict, Tuple


class CubeAdapter:
    """适配器类，将项目中的魔方状态转换为两阶段算法所需格式"""

    # 颜色到字符的映射
    COLOR_MAP = {
        (1.0, 0.0, 0.0): 'U',  # 红色 -> U (Up)
        (1.0, 1.0, 0.0): 'R',  # 黄色 -> R (Right)
        (0.0, 1.0, 0.0): 'F',  # 绿色 -> F (Front)
        (1.0, 0.5, 0.0): 'D',  # 橙色 -> D (Down)
        (1.0, 1.0, 1.0): 'L',  # 白色 -> L (Left)
        (0.0, 0.0, 1.0): 'B',  # 蓝色 -> B (Back)
    }

    # 面的索引映射 
    FACE_INDICES = {
        'U': [(-1, 1, -1), (0, 1, -1), (1, 1, -1),
              (-1, 1, 0), (0, 1, 0), (1, 1, 0),
              (-1, 1, 1), (0, 1, 1), (1, 1, 1)],
        'R': [(1, 1, 1), (1, 1, 0), (1, 1, -1),
              (1, 0, 1), (1, 0, 0), (1, 0, -1),
              (1, -1, 1), (1, -1, 0), (1, -1, -1)],
        'F': [(-1, 1, 1), (0, 1, 1), (1, 1, 1),
              (-1, 0, 1), (0, 0, 1), (1, 0, 1),
              (-1, -1, 1), (0, -1, 1), (1, -1, 1)],
        'D': [(-1, -1, 1), (0, -1, 1), (1, -1, 1),
              (-1, -1, 0), (0, -1, 0), (1, -1, 0),
              (-1, -1, -1), (0, -1, -1), (1, -1, -1)],
        'L': [(-1, 1, -1), (-1, 1, 0), (-1, 1, 1),
              (-1, 0, -1), (-1, 0, 0), (-1, 0, 1),
              (-1, -1, -1), (-1, -1, 0), (-1, -1, 1)],
        'B': [(1, 1, -1), (0, 1, -1), (-1, 1, -1),
              (1, 0, -1), (0, 0, -1), (-1, 0, -1),
              (1, -1, -1), (0, -1, -1), (-1, -1, -1)]
    }

    FACE_KEY_MAP = {
        'U': '+Y',
        'D': '-Y',
        'L': '-X',
        'R': '+X',
        'F': '+Z',
        'B': '-Z'
    }

    def __init__(self, cube: RubiksCube):
        self.cube = cube

    def get_cube_string(self) -> str:
        """
        将魔方状态转换为两阶段算法所需的字符串格式
        格式: UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
        """
        result = ""

        # 按照 U-R-F-D-L-B 的顺序获取每个面的颜色
        for face_char in ['U', 'R', 'F', 'D', 'L', 'B']:
            face_colors = self._get_face_colors(face_char)
            result += face_colors

        return result

    def _get_face_colors(self, face_char: str) -> str:
        """获取指定面的所有颜色字符"""
        face_indices = self.FACE_INDICES[face_char]
        colors = ""

        for pos in face_indices:
            cubie = self.cube.cubies.get(pos)
            if cubie:
                # 获取对应面的颜色
                face_key = self.FACE_KEY_MAP[face_char]
                if face_key in cubie.colors:
                    color_rgb = cubie.colors[face_key]
                    color_char = self.COLOR_MAP.get(color_rgb, 'U')  # 默认为U色
                    colors += color_char
                else:
                    # 如果找不到对应面，使用默认颜色
                    colors += 'U'
            else:
                colors += 'U'  # 默认为U色

        return colors
