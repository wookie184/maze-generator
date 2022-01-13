from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple

EdgeType = Tuple[int, int]


class MediaFormat(Enum):
    MP4 = auto()
    GIF = auto()
    PNG = auto()
    JPEG = auto()
    JPG = JPEG

    @classmethod
    def from_string(cls, string: str) -> MediaFormat:
        try:
            return cls.__members__[string]
        except KeyError:
            raise ValueError("Invalid MediaFormat string")

    @classmethod
    def formats(cls) -> List[str]:
        return list(cls.__members__.keys())


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


class ColourInfo(NamedTuple):
    start: int
    speed: float


class SaveOption(NamedTuple):
    format: MediaFormat
    path: Optional[Path]


class Speed(NamedTuple):
    frames_per_second: int
    steps_per_frame: int
