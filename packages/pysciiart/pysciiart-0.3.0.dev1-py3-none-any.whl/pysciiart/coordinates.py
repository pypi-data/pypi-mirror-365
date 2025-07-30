import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


@dataclass(frozen=True)
class Position:
    x: int
    y: int


class PathStep(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    TURN = 2


class Path(List[Tuple[PathStep, Position]]):
    def __init__(self, start: Position, end: Position) -> None:
        super().__init__()
        self.start = start
        self.end = end

        self._generate_path()

    def _generate_path(self) -> None:
        start, end = self.start, self.end
        dx = 1 if self.start.x <= self.end.x else -1
        dy = 1 if self.start.y <= self.end.y else -1

        mid_x = math.floor((start.x + end.x) / 2)

        for x in range(start.x, mid_x, dx):
            self.append((PathStep.HORIZONTAL, Position(x, start.y)))

        if start.y == end.y:
            self.append((PathStep.HORIZONTAL, Position(mid_x, start.y)))
        else:
            self.append((PathStep.TURN, Position(mid_x, start.y)))

            for y in range(start.y + dy, end.y, dy):
                self.append((PathStep.VERTICAL, Position(mid_x, y)))

            self.append((PathStep.TURN, Position(mid_x, end.y)))

        for x in range(mid_x + dx, end.x + dx, dx):
            self.append((PathStep.HORIZONTAL, Position(x, end.y)))


@dataclass(frozen=True)
class Size:
    width: int
    height: int


@dataclass(frozen=True)
class Rectangle(Position, Size):
    pass
