from enum import Enum
import array
import random


class State(Enum):
    ALIVE = 1
    DEAD = 0


class Cell:
    x, y = 0, 0
    state = State.DEAD
    color = [0.0, 0.0, 0.0]
    size = 0
    next_action = []

    def __init__(self, x, y, state, color, size):
        self.x = x
        self.y = y
        self.state = state
        self.color = color
        self.size = size

    def draw(self):
        if self.state == State.ALIVE:
            color = [self.color[0], self.color[1], self.color[2]]
        else:
            color = [0.0, 0.0, 0.0]

        return [
            color,
            self.draw_rectangle(self.x, self.y, self.size, self.size)
        ]

    def init(self):
        if len(self.next_action) > 0:
            for action in self.next_action:
                action()
        self.next_action.clear()

    def check_state(self, cells, width, height):
        neighbours = self.get_neighbours(cells, width, height)
        alive_neighbours = neighbours[0]
        dead_neighbours = neighbours[1]

        # Rules
        # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        if self.state == State.ALIVE:
            if alive_neighbours < 2:
                self.next_action = [self.die]
                return

        # Any live cell with two or three live neighbours lives on to the next generation.
        if self.state == State.ALIVE:
            if alive_neighbours == 2 or alive_neighbours == 3:
                # Do nothing
                return

        # Any live cell with more than three live neighbours dies, as if by overpopulation.
        if self.state == State.ALIVE:
            if alive_neighbours > 3:
                self.next_action = [self.die]
                return

        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        if self.state == State.DEAD:
            if alive_neighbours == 3:
                self.next_action = [self.resurrect]
                return

    def die(self):
        self.state = State.DEAD

    def resurrect(self):
        self.state = State.ALIVE

    def get_neighbours(self, cells, width, height):
        alive_neighbours = 0
        dead_neighbours = 0

        # Convert width and height to 0-indexed sizes
        width -= 1
        height -= 1

        color_chance = 0.5
        rand = random.uniform(0.0, 0.1)
        coordinate_map = [
            [1, 0],
            [-1, 0],
            [0, 1],
            [0, -1],
            [1, 1],
            [1, -1],
            [-1, -1],
            [-1, 1]
        ]

        for coordinate in coordinate_map:
            x = self.x + coordinate[0]
            y = self.y + coordinate[1]

            if x > width:
                x = 0
            elif x == 0:
                x = width
            if y > height:
                y = 0
            elif y == 0:
                y = height

            # TODO: Somehow cache the neighbour results so we can skip this whole step for the 'known' cells

            cell = cells[x][y]
            if cell.state == State.ALIVE:
                alive_neighbours += 1
                self.color = cell.color if rand < color_chance else self.color  # Chance to inherit neighbour's color
            else:
                dead_neighbours += 1

        return [alive_neighbours, dead_neighbours]

    def draw_rectangle(self, x, y, _width, _height):
        if x > 0:
            x = x * _width
        if y > 0:
            y = y * _height

        vertices = array.array('f',
                               [
                                   x, y,
                                   x + _width, y,
                                   x + _width, y + _width,
                                   x, y + _height
                               ])

        return vertices
