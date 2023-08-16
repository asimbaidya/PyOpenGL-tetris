import time
from random import choice

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

## show log
SHOW_LOG = True


# for logging and debugging
def log(*args):
    if SHOW_LOG:
        print(*args)


## Color Constants:
WINDOW_BG = (0.1451, 0.1451, 0.20784)
GRID_BG_COLOR = (0.08627, 0.08627, 0.11373)
# GRID_BG_COLOR = (0, 0, 0)
GRID_LINE_COLOR = (1, 0.3, 1)
GRID_LINE_COLOR = (0.1451, 0.1451, 0.20784)
GRID_EMPTY_CELL = (0.03627, 0.08627, 0.031373)
GRID_EMPTY_CELL_ALT = (0.03627, 0.08627, 0.031373)
RED = [1, 0, 0]
COLORS = [
    (1.0, 0.0, 0.0),  # red
    (0.0, 0.0, 1.0),  # blue
    (0.0, 1.0, 0.0),  # green
    (1.0, 1.0, 0.0),  # yellow
    (1.0, 0.0, 1.0),  # magenta
]

# Window Constants:
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 780

## grid width & height
GRID_SIZE = 30

GRID_WIDTH = GRID_SIZE * 20
GRID_HEIGHT = GRID_SIZE * 26

GRID_ROW = GRID_HEIGHT // GRID_SIZE
GRID_COL = GRID_WIDTH // GRID_SIZE

GRID_OFFSET_X = WINDOW_WIDTH - GRID_WIDTH
GRID_OFFSET_Y = 0

log(f"GRID ROW X COL = {GRID_ROW} X {GRID_COL}")


# shapes
SHAPES = [
    [(0, 0), (1, 0), (2, 0), (3, 0)],  # I-shape
    [(0, 1), (1, 1), (2, 1), (2, 0)],  # L-rev shape
    [(0, 0), (1, 0), (0, 1), (1, 1)],  # square shape
    [(0, 1), (1, 1), (1, 0), (2, 0)],  # z-shape
    [(0, 0), (1, 0), (1, 1), (2, 0)],  # t-shape
    [(0, 1), (1, 1), (1, 0), (2, 1)],  # s-shape
]


class TetrisGame:
    def __init__(self):
        # using a matrix for whole window
        self.window = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
        # change whole window background color
        self.window[:, :, :] = np.array(WINDOW_BG) * 255

        # extracting grid portion from matrix
        self.grid = self.window[
            GRID_OFFSET_Y : GRID_OFFSET_Y + GRID_HEIGHT,
            GRID_OFFSET_X : GRID_OFFSET_X + GRID_WIDTH,
            :,
        ]
        # change grid background color
        self.grid[:, :, :] = np.array((0.8, 0.8, 8.0)) * 255

        # for - current shape
        self.current_shape = choice(SHAPES)
        self.current_pos = (GRID_ROW - 1, GRID_COL // 2)
        self.current_color = choice(COLORS)

        # collision detection
        self.is_collided_bottom = True
        self.is_collided_left = False
        self.is_collided_right = False
        self.is_collided_left_wall = False
        self.is_collided_right_wall = False

        self.bool_grid = np.full((GRID_ROW, GRID_COL), False, dtype=bool)
        self.filled_grid = np.full(
            (GRID_ROW, GRID_COL, 3), GRID_EMPTY_CELL, dtype=np.float64
        )

        self.is_game_over = False
        self.score = 0

    def change_shape(self):
        prev_shape = self.current_shape
        self.current_shape = choice(SHAPES)
        while prev_shape == self.current_shape:
            self.current_shape = choice(SHAPES)

        self.update_current_shape()

    def update_current_shape(self):
        self.change_grid_bg()
        self.fill_occupied_grid()
        for x, y in self.current_shape:
            self.fill_grid(
                self.current_color,
                x + self.current_pos[0],
                y + self.current_pos[1],
            )
        log(f"🖌filling {x + self.current_pos[0]} {y + self.current_pos[1]}")

    def generate_new_shape(self):
        log("generating new shape")
        self.current_shape = choice(SHAPES)
        self.current_color = choice(COLORS)

    def fill_grid(self, color, x, y):
        x = x * GRID_SIZE
        y = y * GRID_SIZE
        xe = x + GRID_SIZE
        ye = y + GRID_SIZE
        self.grid[x:xe, y:ye, :] = np.array(color) * 255

    def fill_occupied_grid(self):
        log("() filling occupied grid")

        for i in range(GRID_ROW):
            for j in range(GRID_COL):
                if self.bool_grid[i, j]:
                    self.fill_grid(self.filled_grid[i, j], i, j)

        if self.is_game_over:
            color = np.random.uniform(0.2, 0.3, 3)
            for i in range(GRID_ROW):
                for j in range(GRID_COL):
                    if not self.bool_grid[i, j]:
                        self.fill_grid(color, i, j)

    def change_grid_bg(self):
        log("() changing grid bg")
        self.grid[:, :, :] = np.array(GRID_BG_COLOR) * 255

    def detect_bottom_collision(self):
        x, y = self.current_pos
        x_down = x - 1

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_down = (
            min(GRID_ROW - 1, self.current_shape[0][0] + x_down),
            self.current_shape[0][1] + y,
        )
        c2_down = (
            min(GRID_ROW - 1, self.current_shape[1][0] + x_down),
            self.current_shape[1][1] + y,
        )
        c3_down = (
            min(GRID_ROW - 1, self.current_shape[2][0] + x_down),
            self.current_shape[2][1] + y,
        )
        c4_down = (
            min(GRID_ROW - 1, self.current_shape[3][0] + x_down),
            self.current_shape[3][1] + y,
        )

        flag_collide = False
        if c1[0] == 0 or c2[0] == 0 or c3[0] == 0 or c4[0] == 0:
            flag_collide = True

        if (
            self.bool_grid[c1_down]
            or self.bool_grid[c2_down]
            or self.bool_grid[c3_down]
            or self.bool_grid[c4_down]
        ):
            flag_collide = True

        if flag_collide:
            log("️🟥🟥🟥🟥🟥🟥🟥Bottom collided🟥🟥🟥🟥🟥🟥")
            self.is_collided_bottom = True
            self.update_filled_grid(c1, c2, c3, c4)

    def detect_left_collision(self):
        x, y = self.current_pos
        y_left = y - 1

        log("(x,y):", x, y)
        log("(x,y_left):", x, y_left)

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_left = (
            min(self.current_shape[0][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[0][1] + y_left),
        )
        c2_left = (
            min(self.current_shape[1][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[1][1] + y_left),
        )
        c3_left = (
            min(self.current_shape[2][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[2][1] + y_left),
        )
        c4_left = (
            min(self.current_shape[3][0] + x, GRID_ROW - 1),
            max(0, self.current_shape[3][1] + y_left),
        )

        flag_collide = False
        #
        if c1[1] == 0 or c2[1] == 0 or c3[1] == 0 or c4[1] == 0:
            flag_collide = True

        log("c1_left:", c1_left)
        log("c2_left:", c2_left)
        log("c3_left:", c3_left)
        log("c4_left:", c4_left)

        if (
            self.bool_grid[c1_left]
            or self.bool_grid[c2_left]
            or self.bool_grid[c3_left]
            or self.bool_grid[c4_left]
        ):
            flag_collide = True

        if flag_collide:
            log("️🟥🟥🟥🟥🟥🟥🟥Left collided🟥🟥🟥🟥🟥🟥")
            self.is_collided_left = True

    def detect_right_collision(self):
        x, y = self.current_pos
        y_right = y + 1

        c1 = self.current_shape[0][0] + x, self.current_shape[0][1] + y
        c2 = self.current_shape[1][0] + x, self.current_shape[1][1] + y
        c3 = self.current_shape[2][0] + x, self.current_shape[2][1] + y
        c4 = self.current_shape[3][0] + x, self.current_shape[3][1] + y

        c1_right = (
            min(self.current_shape[0][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[0][1] + y_right),
        )
        c2_right = (
            min(self.current_shape[1][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[1][1] + y_right),
        )
        c3_right = (
            min(self.current_shape[2][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[2][1] + y_right),
        )
        c4_right = (
            min(self.current_shape[3][0] + x, GRID_ROW - 1),
            min(GRID_COL - 1, self.current_shape[3][1] + y_right),
        )

        flag_collide = False
        if (
            c1[1] == GRID_COL - 1
            or c2[1] == GRID_COL - 1
            or c3[1] == GRID_COL - 1
            or c4[1] == GRID_COL - 1
        ):
            flag_collide = True

        if (
            self.bool_grid[c1_right]
            or self.bool_grid[c2_right]
            or self.bool_grid[c3_right]
            or self.bool_grid[c4_right]
        ):
            flag_collide = True

        if flag_collide:
            log("️🟥🟥🟥🟥🟥🟥🟥Right collided🟥🟥🟥🟥🟥🟥")
            self.is_collided_right = True

    def game_restart(self):
        self.bool_grid = np.full((GRID_ROW, GRID_COL), False, dtype=bool)
        self.filled_grid = np.full(
            (GRID_ROW, GRID_COL, 3), GRID_EMPTY_CELL, dtype=np.float64
        )
        self.is_game_over = False
        self.score = 0

    def detect_game_over(self, cell_one, cell_two, cell_three, cell_four):
        if self.is_game_over:
            print("Enter (space) for restart")
            return

        if (
            cell_one[0] >= GRID_ROW - 1
            or cell_two[0] >= GRID_ROW - 1
            or cell_three[0] >= GRID_ROW - 1
            or cell_four[0] >= GRID_ROW - 1
        ):
            self.is_game_over = True
            for cell in [cell_one, cell_two, cell_three, cell_four]:
                if cell[0] <= GRID_ROW - 1:
                    self.filled_grid[cell[0], cell[1]] = self.current_color
                    self.bool_grid[cell] = True

            print("🔥🔥🔥🔥🔥🔥🔥🔥🔥Game Over🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
            print("score:", self.score)
            print("Enter (space) for restart")
            return

    def update_score(self):
        # BUG: fix score update why only sinlgle row get's updated
        # check if row of bool_grid is full then increase score by grid column size
        # update that row with row above it & check

        if self.is_game_over:
            return

        for i in range(GRID_ROW):
            if all(self.bool_grid[i]):
                self.score += GRID_COL
                self.bool_grid[i] = False

                # down down
                for j in range(i + 1, GRID_ROW):
                    self.bool_grid[j - 1] = self.bool_grid[j]
                    self.filled_grid[j - 1] = self.filled_grid[j]

                # unset top row
                self.bool_grid[GRID_ROW - 1] = False

        log("🔃 Score updating", self.score)

    def update_filled_grid(self, c1, c2, c3, c4):
        self.detect_game_over(c1, c2, c3, c4)
        if self.is_game_over:
            return

        self.filled_grid[c1] = self.current_color
        self.filled_grid[c2] = self.current_color
        self.filled_grid[c3] = self.current_color
        self.filled_grid[c4] = self.current_color

        self.bool_grid[c1] = True
        self.bool_grid[c2] = True
        self.bool_grid[c3] = True
        self.bool_grid[c4] = True

        self.update_score()
        self.update_current_shape()

    def place_on_grid(self):
        self.generate_new_shape()
        self.is_collided_bottom = False
        self.current_pos = (GRID_ROW, GRID_COL // 2)

        self.update_current_shape()

    def move_auto_down(self):
        if self.is_game_over:
            return

        self.detect_bottom_collision()

        if self.is_collided_bottom:
            self.place_on_grid()
            return

        log("🔻 Down")
        self.current_pos = (
            self.current_pos[0] - 1,
            self.current_pos[1],
        )

        self.update_current_shape()

    def move_left(self):
        # need tweek
        self.detect_left_collision()
        if self.is_collided_left:
            self.update_current_shape()  # ??
            self.is_collided_left = False
            return

        self.current_pos = (
            self.current_pos[0],
            self.current_pos[1] - 1,
        )

        self.update_current_shape()

    def move_right(self):
        self.detect_right_collision()

        if self.is_collided_right:
            self.update_current_shape()  # ??
            self.is_collided_right = False
            return

        self.current_pos = (
            self.current_pos[0],
            self.current_pos[1] + 1,
        )
        self.update_current_shape()

    def move_bottom(self):
        for i in range(GRID_ROW + 4):
            self.detect_bottom_collision()

            if self.is_collided_bottom:
                log("💥 collided bottom")
                self.place_on_grid()
                return

            log("🔻++ Down")
            self.current_pos = (
                self.current_pos[0] - 1,
                self.current_pos[1],
            )
            self.update_current_shape()


def keyboard(key, _x, _y):
    log(f"(fn) keyboard interrupt key: {key.decode('utf-8')}")
    # using useless mouse position
    _, _ = _x, _y

    avoid_redisplay = False
    if key.decode("utf-8") in "qhlj ":
        # update grid background color as shape will be moved
        game.change_grid_bg()
        game.fill_occupied_grid()

    if game.is_game_over and key != b" ":
        print("Enter (space) for restart")

    # map action to key
    if key == b"q":
        # Escape key to exit
        print("Thank for playing with my life 423🙂")
        glutDestroyWindow(glutGetWindow())
        avoid_redisplay = True
    elif key == b"h":
        game.move_left()
    elif key == b"l":
        game.move_right()
    elif key == b"j":
        game.move_bottom()
    elif key == b" ":
        if game.is_game_over:
            game.game_restart()
        else:
            game.change_shape()

    if not avoid_redisplay:
        glutPostRedisplay()


def draw_grid_lines():
    log("(fn) 🪟grid line drawing")

    # draw vertical lines in grid
    for i in range(0, WINDOW_HEIGHT):
        for j in range(WINDOW_WIDTH - GRID_WIDTH, WINDOW_WIDTH, GRID_SIZE):
            game.window[i, j] = np.array(GRID_LINE_COLOR) * 255

    # draw horizontal lines in grid
    for i in range(0, WINDOW_HEIGHT, GRID_SIZE):
        for j in range(WINDOW_WIDTH - GRID_WIDTH, WINDOW_WIDTH):
            game.window[i, j] = np.array(GRID_LINE_COLOR) * 255


def fill_buffer():
    # takes game.window matrix and draw in one step
    # only this function apply changes in the screen, rest of the method only
    # manuplate game.window matrix

    glClear(GL_COLOR_BUFFER_BIT)
    glRasterPos2f(-1, -1)
    glDrawPixels(WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, game.window)
    glutSwapBuffers()


def display():
    # display all the components

    # draw grids in right side
    draw_grid_lines()

    # update the matrix into display
    fill_buffer()


def update(value):
    game.change_grid_bg()
    game.fill_occupied_grid()
    game.move_auto_down()

    glutTimerFunc(1000, update, 0)
    glutPostRedisplay()


def reshape(width, height):
    # ?? what this does
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)


def main():
    # ctrl+c && ctrl+v
    glutInit(sys.argv)
    # ctrl+c && ctrl+v
    glutInitDisplayMode(GLUT_RGB)
    # ctrl+c && ctrl+v
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)

    # this set window position (0,0) means strt from top-left
    # then oftet determine the exact position of start from top-left
    glutInitWindowPosition(100, 100)

    # (`opengl` is important for xmonad to ingnore tiling)
    wind = glutCreateWindow(b"opengl")
    # wind = glutCreateWindow(b"Tetris")

    # window background color (does not matter really)
    # glClearColor(1.0, 0, 0, 1.0)
    # glClearColor(*WINDOW_BG, 1.0)

    # display maybe, god knows
    glutDisplayFunc(display)

    # what this does?
    # glutReshapeFunc(reshape)

    # to handle keyboard control
    glutKeyboardFunc(keyboard)

    # timer function
    glutTimerFunc(0, update, 0)

    # game.generate_new_shape()
    glutMainLoop()


if __name__ == "__main__":
    game = TetrisGame()
    main()
