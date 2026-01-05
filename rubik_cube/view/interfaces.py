# view/interfaces.py
from typing import Tuple, Dict
from abc import ABC, abstractmethod


class ICubie(ABC):
    """View层期望的Cubie接口 - Model层必须实现"""

    @property
    @abstractmethod
    def position(self) -> Tuple[int, int, int]:
        """返回[-1,0,1]坐标，如(1, -1, 0)"""
        pass

    @property
    @abstractmethod
    def colors(self) -> Dict[str, Tuple[float, float, float]]:
        """返回{'+X': (1,1,0), '-Z': (0,0,1), ...}"""
        pass

    @property
    @abstractmethod
    def animation_matrix(self) -> 'list[float]':
        """返回4x4旋转矩阵（动画时）或单位矩阵"""
        pass