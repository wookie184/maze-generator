import random
from collections import deque
from typing import List, Literal, Tuple, Union

import networkx as nx

from .constants import EdgeType, Return, ReturnType


def create_grid(width: int, height: int) -> nx.Graph:
    grid = nx.Graph()

    last_x = None
    for x_pos in range(width):
        last_y = None
        for y_pos in range(height):
            grid.add_node((x_pos, y_pos))

            if last_x is not None:
                grid.add_edge((last_x, y_pos), (x_pos, y_pos))
            if last_y is not None:
                grid.add_edge((x_pos, last_y), (x_pos, y_pos))

            last_y = y_pos
        last_x = x_pos
    return grid


def get_middle(edge: Tuple[EdgeType, EdgeType]) -> EdgeType:
    (x1, y1), (x2, y2) = edge
    return (2 * min(x1, x2) + abs(x1 - x2)), (2 * min(y1, y2) + abs(y1 - y2))


def to_grid_coords(node: EdgeType) -> EdgeType:
    x, y = node
    return x * 2, y * 2


class MazeGenerator:
    def __init__(self, width: int, height: int):
        self.width = width // 2 + 1
        self.height = height // 2 + 1
        self.grid = create_grid(self.width, self.height)
        self.visited = set(((0, 0),))
        self.stack = deque(((0, 0),))

    def step(self) -> Union[Literal[ReturnType.COMPLETED], Return]:
        if len(self.visited) == self.width * self.height:
            return ReturnType.COMPLETED
        pos = self.stack.popleft()
        neighbors = [n for n in self.grid.neighbors(pos) if n not in self.visited]
        if not neighbors:
            n = self.stack[0]
            return Return(
                ReturnType.BACKTRACK,
                (to_grid_coords(pos), get_middle((pos, n)), to_grid_coords(n)),
            )

        n = random.choice(neighbors)
        self.stack.appendleft(pos)
        self.stack.appendleft(n)
        self.visited.add(n)
        self.grid.remove_edge(pos, n)

        return Return(
            ReturnType.NEW,
            (to_grid_coords(pos), get_middle((pos, n)), to_grid_coords(n)),
        )

    @property
    def walls(self) -> List[EdgeType]:
        res = []
        for edge in self.grid.edges:
            res.append(get_middle(edge))
        return res
