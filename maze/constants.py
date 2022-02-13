from __future__ import annotations

from enum import Enum, auto
from typing import NamedTuple, Tuple

EdgeType = Tuple[int, int]


class ReturnType(Enum):
    COMPLETED = auto()
    BACKTRACK = auto()
    NEW = auto()


class Return(NamedTuple):
    type: ReturnType
    value: Tuple[EdgeType, EdgeType, EdgeType]


class Size(NamedTuple):
    width: int
    height: int
