# main.py
import sys
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from view.renderer import Renderer
from model.cube import RubiksCube
from control.animation import AnimationQueue
from control.input_handler import InputHandler
from ui.ui_manager import UIManager  
from control.solver_controller import SolverController

# 全局实例
cube = RubiksCube()
renderer = Renderer()
animation_queue = AnimationQueue(cube)
input_handler = InputHandler(cube, animation_queue)
ui_manager = UIManager(800, 600)  # UI管理器


# 绑定相机
input_handler.bind_camera(renderer.camera)
# 绑定输入处理器到渲染器
renderer.bind_input_handler(input_handler)
# 绑定渲染器到输入处理器
input_handler.bind_renderer(renderer)
# 新增：绑定UI管理器
input_handler.bind_ui_manager(ui_manager)  
renderer.bind_ui_manager(ui_manager) 

# 帧率控制
last_time = time.time()


def idle():
    """空闲回调，持续刷新窗口以支持动画"""
    glutPostRedisplay()


def display():
    global last_time

    # 计算delta_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    # 更新动画
    animation_queue.update(delta_time)

    # 渲染
    renderer.render(cube.get_cubies())
    glutSwapBuffers()

    # 如果动画未完成，继续刷新
    if animation_queue.current_animation:
        glutPostRedisplay()


def keyboard(key, x, y):
    input_handler.keyboard(key, x, y)


def mouse(button, state, x, y):
    # 先让输入处理器处理
    if not input_handler.mouse(button, state, x, y):
        # 如果输入处理器没有处理，直接刷新显示
        glutPostRedisplay()


def motion(x, y):
    input_handler.motion(x, y)


def reshape(width, height):
    """窗口大小改变时调用"""
    # 更新渲染器
    renderer.width = width
    renderer.height = height

    # 更新UI管理器
    ui_manager.resize(width, height)

    # 标记需要重绘
    glutPostRedisplay()



def main():
    global cube, renderer, animation_queue, input_handler, ui_manager

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Interactive Rubik's Cube")

    # 初始化所有组件
    cube = RubiksCube()
    renderer = Renderer()
    animation_queue = AnimationQueue(cube)
    input_handler = InputHandler(cube, animation_queue)
    ui_manager = UIManager(800, 600)

    # 创建求解控制器
    solver_controller = SolverController(cube, animation_queue)  # 新增

    # 绑定组件
    input_handler.bind_camera(renderer.camera)
    input_handler.bind_renderer(renderer)
    input_handler.bind_ui_manager(ui_manager)
    input_handler.bind_solver_controller(solver_controller)  # 新增
    renderer.bind_input_handler(input_handler)
    renderer.bind_ui_manager(ui_manager)

    # 初始化OpenGL
    renderer.initialize_gl()

    # 设置回调
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutMouseWheelFunc(input_handler.scroll)
    glutReshapeFunc(reshape)

    glutMainLoop()



if __name__ == '__main__':
    main()
