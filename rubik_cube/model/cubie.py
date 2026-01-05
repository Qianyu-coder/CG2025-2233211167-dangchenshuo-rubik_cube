# model/cubie.py
from typing import Dict, Tuple


class Cubie:
    """单个魔方块"""

    # 魔方颜色映射
    FACE_COLORS = {
        '+X': (1.0, 1.0, 0.0),  # 右面 - 黄色
        '-X': (1.0, 1.0, 1.0),  # 左面 - 白色
        '+Y': (1.0, 0.0, 0.0),  # 顶面 - 红色
        '-Y': (1.0, 0.5, 0.0),  # 底面 - 橙色
        '+Z': (0.0, 1.0, 0.0),  # 前面 - 绿色
        '-Z': (0.0, 0.0, 1.0),  # 后面 - 蓝色
    }

    def __init__(self, position: Tuple[int, int, int]):
        """
        position: (x,y,z) ∈ {-1,0,1}
        """
        self.position = position
        self.colors = self._init_colors(position)
        # 用于动画的旋转矩阵
        self.animation_matrix = None  # 将来由Control层设置

    def _init_colors(self, pos: Tuple[int, int, int]) -> Dict[str, Tuple[float, float, float]]:
        """初始化所有6个面的颜色"""
        colors = {}
        x, y, z = pos

        # 为所有面设置颜色，表面使用标准颜色，内部面使用标准颜色
        for face_key in ['+X', '-X', '+Y', '-Y', '+Z', '-Z']:
            # 设置颜色
            colors[face_key] = self.FACE_COLORS[face_key]

        return colors

    # 以下三个方法供View层调用，实现ICubie接口
    def get_position(self) -> Tuple[int, int, int]:
        return self.position

    def get_colors(self) -> Dict[str, Tuple[float, float, float]]:
        return self.colors

    def get_animation_matrix(self):
        return self.animation_matrix
