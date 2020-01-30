import math
import random
from ctypes import create_string_buffer
from time import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from profilehooks import profile

from cell import Cell, State

# ----------------------
# Configurable settings
window_width, window_height = 800, 600  # Width, Height of the window
cell_size = 4  # How many pixels one Cell is
alive_chance = 8  # Chance to start alive
seed = random.seed = time()
# ----------------------

# ASCII characters
ESCAPE = as_8_bit('\033')
SPACE = as_8_bit(' ')

# From venv/Lib/site-packages/OpenGL/platform/win32.py
# somehow they are not recognized directly as constants...
GLUT_STROKE_ROMAN = ctypes.c_void_p(0)
GLUT_STROKE_MONO_ROMAN = ctypes.c_void_p(1)
GLUT_BITMAP_9_BY_15 = ctypes.c_void_p(2)
GLUT_BITMAP_8_BY_13 = ctypes.c_void_p(3)
GLUT_BITMAP_TIMES_ROMAN_10 = ctypes.c_void_p(4)
GLUT_BITMAP_TIMES_ROMAN_24 = ctypes.c_void_p(5)
GLUT_BITMAP_HELVETICA_10 = ctypes.c_void_p(6)
GLUT_BITMAP_HELVETICA_12 = ctypes.c_void_p(7)
GLUT_BITMAP_HELVETICA_18 = ctypes.c_void_p(8)

window = 0

top_bar_height = 10
height = math.floor(window_height / cell_size) - top_bar_height
width = math.floor(window_width / cell_size)
cell_rectangles = []
cells = []
restart_flag = False

total_frames, total_updates = 0, 0
last_fps_check, last_ups_check = 0, 0
current_fps, current_ups = 0, 0

start_time = 0

debug_count = 0


@profile
def draw():
    global debug_count, total_frames, last_fps_check, current_fps, current_ups

    # FPS Check
    total_frames += 1
    current_time = math.floor(time())
    if last_fps_check < current_time:  # 1 second has passed
        current_fps = total_frames
        total_frames = 0
    last_fps_check = current_time

    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen

    refresh2d(window_width, window_height)  # make camera 2d

    glEnableClientState(GL_VERTEX_ARRAY)
    for cell in cell_rectangles:
        glColor3f(cell[0][0], cell[0][1], cell[0][2])
        glVertexPointer(2, GL_FLOAT, 0, cell[1])
        glDrawArrays(GL_QUADS, 0, 4)
    glDisableClientState(GL_VERTEX_ARRAY)

    draw_text("Seed: {}, FPS: {}, UPS: {}, Time running: {} seconds".format(random.seed, current_fps, current_ups, (math.floor(time() - start_time))), 10, window_height - (top_bar_height + 10), [1.0, 1.0, 1.0])
    print("Seed: {}, FPS: {}, UPS: {}, Time running: {} seconds".format(random.seed, current_fps, current_ups, (math.floor(time() - start_time))))

    glutSwapBuffers()  # important for double buffering (??)

    # debug_count += 1
    # if debug_count == 1:
    #     exit(0)


def draw_text(value, x, y, color):
    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(x, y)
    lines = 0
    for character in value:
        if character == '\n':
            glRasterPos2f(x, y - (lines * 18))
        else:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(character))


def refresh2d(_width, _height):
    glViewport(0, 0, _width, _height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, _width, 0.0, _height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


@profile
def update():
    global restart_flag, total_updates, last_ups_check, current_ups

    # UPS Check
    total_updates += 1
    current_time = math.floor(time())
    if last_ups_check < current_time:  # 1 second has passed
        current_ups = total_updates
        total_updates = 0
    last_ups_check = current_time

    if restart_flag:
        restart_flag = False
        cells.clear()
        start()
        return

    cell_rectangles.clear()

    deaths = 0
    # for x in range(0, len(cells)):
    #     for y in range(0, len(cells[x])):
    #         cell = cells[x][y]
    #         cell.init()
    #         if cell.state == State.DEAD:
    #             deaths += 1

    if deaths == len(cells) * len(cells[0]):
        restart()
        return

    # TODO: These loops cause the 1 FPS issue
    for x in range(0, len(cells)):
        for y in range(0, len(cells[x])):
            cell = cells[x][y]
            cell.check_state(cells, width, height)
            cell_rectangle = cell.draw()
            cell_rectangles.append([cell_rectangle[0], cell_rectangle[1].tostring()])

    glutPostRedisplay()


def restart():
    global restart_flag
    restart_flag = True


def start():
    global cells, start_time
    start_time = math.floor(time())

    cells = [[0 for y in range(height)] for x in range(width)]

    for x in range(0, len(cells)):
        for y in range(0, len(cells[0])):
            color = random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)
            state = State.ALIVE if random.uniform(0.0, 1.0) < (alive_chance / 100) else State.DEAD

            # Glider
            # if (x == 13 and y == height-10)\
            #         or (x == 13 and y == height-11)\
            #         or (x == 13 and y == height-12)\
            #         or (x == 12 and y == height-12)\
            #         or (x == 11 and y == height-11):
            #     state = State.ALIVE
            # else:
            #     state = State.DEAD

            cells[x][y] = Cell(x, y, state, color, cell_size)


def key_up(key, x, y):
    if key == ESCAPE:
        exit()
    elif key == SPACE:
        restart()
    else:
        print("key: {} pressed".format(key))


def init():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Game of Life")
    glutDisplayFunc(draw)
    glutIdleFunc(update)
    glutKeyboardUpFunc(key_up)

    start()

    glutMainLoop()


init()
