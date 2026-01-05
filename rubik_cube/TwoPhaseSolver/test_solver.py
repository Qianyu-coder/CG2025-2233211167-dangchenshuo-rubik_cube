# 在 test_solver.py 中修改 apply_moves_to_cube 函数
import sys
import os

# 添加 TwoPhaseSolver 到路径
solver_path = os.path.join(os.path.dirname(__file__))
sys.path.append(solver_path)

from solver import solve
from face import FaceCube
from enums import Color
import cubie  # 导入整个 cubie 模块以访问 basicMoveCube


def apply_moves_to_cube(cube_string, solution_string):
    """
    将解法步骤应用到魔方并返回最终状态

    Args:
        cube_string: 初始魔方状态字符串
        solution_string: solve函数返回的解法字符串

    Returns:
        str: 应用解法后的魔方状态字符串
    """
    # 解析解法步骤
    # 移除最后的步数信息 "(xxf)"
    if '(' in solution_string:
        solution_string = solution_string[:solution_string.rfind('(')].strip()

    moves = solution_string.split() if solution_string else []

    # 创建初始魔方状态
    fc = FaceCube()
    fc.from_string(cube_string)

    # 定义移动映射
    move_mapping = {
        'U1': (Color.U, 1), 'U2': (Color.U, 2), 'U3': (Color.U, 3),
        'R1': (Color.R, 1), 'R2': (Color.R, 2), 'R3': (Color.R, 3),
        'F1': (Color.F, 1), 'F2': (Color.F, 2), 'F3': (Color.F, 3),
        'D1': (Color.D, 1), 'D2': (Color.D, 2), 'D3': (Color.D, 3),
        'L1': (Color.L, 1), 'L2': (Color.L, 2), 'L3': (Color.L, 3),
        'B1': (Color.B, 1), 'B2': (Color.B, 2), 'B3': (Color.B, 3),
    }

    # 转换为立方体表示
    cc = fc.to_cubie_cube()

    # 应用每个移动
    for move in moves:
        if move in move_mapping:
            face, turns = move_mapping[move]
            # 应用指定次数的转动
            for _ in range(turns):
                cc.multiply(cubie.basicMoveCube[face])  # 正确访问 basicMoveCube

    # 转换回面状态并返回字符串
    final_fc = cc.to_facelet_cube()
    return final_fc.to_string()


# 测试用例
test_cube = "UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB"

print("测试魔方求解...")
result = solve(test_cube, 50, 10)
print(f"求解结果: {result}")

# 获取求解后的状态
if result and not result.startswith("Error"):
    final_state = apply_moves_to_cube(test_cube, result)
    print(f"求解后魔方状态: {final_state}")

    # 验证是否为已解决状态
    solved_state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    if final_state == solved_state:
        print("✓ 魔方已成功求解至已解决状态")
    else:
        print("✗ 魔方未正确求解")
        print(f"期望状态: {solved_state}")
else:
    print("求解失败，无法获取最终状态")
