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

    @classmethod
    def from_string(cls, string: str) -> MediaFormat:
        if string.upper() == "jpg":
            return cls.JPEG
        for e in cls:
            if e.name == string.lower():
                return e
        raise ValueError()

    @classmethod
    def formats(cls) -> List[str]:
        return [e.name for e in cls]


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
