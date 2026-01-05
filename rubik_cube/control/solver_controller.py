# control/solver_controller.py
from control.cube_adapter import CubeAdapter
from model.cube import RubiksCube
from control.animation import AnimationQueue
import sys
import os


class SolverController:
    """控制两阶段算法求解的控制器"""

    def __init__(self, cube: RubiksCube, animation_queue: AnimationQueue):
        self.cube = cube
        self.animation_queue = animation_queue
        self.adapter = CubeAdapter(cube)
        self.solver = None
        self._initialize_solver()

    def _initialize_solver(self):
        """初始化两阶段求解器"""
        try:
            # 添加两阶段算法路径
            solver_path = os.path.join(os.path.dirname(__file__), '..', 'TwoPhaseSolver')
            if solver_path not in sys.path:
                sys.path.insert(0, solver_path)

            # 导入两阶段算法模块
            from solver import solve
            self.solve_func = solve
            print("两阶段求解器初始化成功")
        except ImportError as e:
            print(f"无法导入两阶段求解器: {e}")
            self.solve_func = None

    def solve_cube(self) -> list:
        """
        使用两阶段算法求解魔方，并将结果添加到动画队列
        返回求解步骤列表
        """
        if not self.solve_func:
            print("两阶段求解器未初始化")
            return []

        try:
            # 获取魔方状态字符串
            cube_string = self.adapter.get_cube_string()
            print(f"魔方状态: {cube_string}")

            # 验证魔方状态长度
            if len(cube_string) != 54:
                print(f"错误：魔方状态字符串长度不正确，应为54，实际为{len(cube_string)}")
                return []

            # 调用两阶段算法求解
            solution_str = self.solve_func(cube_string, 50, 10)  # max_length=20, timeout=5秒
            print(f"求解结果: {solution_str}")

            # 检查是否有错误信息
            if solution_str and "Error" in solution_str:
                print(f"求解器返回错误: {solution_str}")
                return []

            # 解析解法步骤
            moves = self._parse_solution(solution_str)

            # 验证移动序列的有效性
            valid_moves = self._validate_moves(moves)
            if not valid_moves:
                print("求解结果包含无效移动")
                return []

            # 将解法添加到动画队列
            if valid_moves:
                self.animation_queue.add_solution(valid_moves)
                print(f"已添加 {len(valid_moves)} 步解法到动画队列")
            else:
                print("未找到有效解法")

            return valid_moves

        except Exception as e:
            print(f"求解过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_solution(self, solution_str: str) -> list:
        """
        解析求解器返回的字符串为移动序列
        """
        if not solution_str:
            return []

        # 移除最后的步数信息 "(xxf)"
        if '(' in solution_str:
            solution_str = solution_str[:solution_str.rfind('(')].strip()

        # 分割成单独的移动
        moves = solution_str.split() if solution_str else []
        return moves

    def _validate_moves(self, moves: list) -> list:
        """
        验证移动序列的有效性，专门适配两阶段算法的数字表示法
        """
        if not moves:
            return []

        valid_faces = {'U', 'R', 'F', 'D', 'L', 'B'}
        validated_moves = []

        for move in moves:
            if not move or len(move) < 2:
                continue

            face = move[0].upper()
            # 检查是否为有效的面
            if face not in valid_faces:
                print(f"警告：发现无效移动面 '{face}' 在移动 '{move}' 中")
                return []

            # 检查是否为有效的数字修饰符
            if len(move) >= 2 and move[1].isdigit():
                modifier = move[1]
                if modifier not in ["1", "2", "3"]:
                    print(f"警告：发现无效移动修饰符 '{modifier}' 在移动 '{move}' 中")
                    return []
            else:
                print(f"警告：移动 '{move}' 不符合数字表示法格式")
                return []

            validated_moves.append(move)

        return validated_moves

