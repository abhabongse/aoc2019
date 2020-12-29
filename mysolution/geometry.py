from __future__ import annotations

import math
from typing import Literal, NamedTuple, SupportsFloat, TypeVar, Union

T = TypeVar('T', bound=SupportsFloat)
TurnCommand = Union[Literal['ahead', 'bow', 'left', 'port', 'u-turn', 'stern', 'right', 'starboard'], int]

TURN_ANGLES = {
    'ahead': 0,
    'bow': 0,
    'left': 90,
    'port': 90,
    'u-turn': 180,
    'stern': 180,
    'right': 270,
    'starboard': 270,
}


class Vec(NamedTuple):
    """
    Two-dimensional vector object.
    """
    x: int
    y: int

    def __pos__(self) -> Vec:
        return self

    def __neg__(self) -> Vec:
        return Vec(-self.x, -self.y)

    def __add__(self, other: Vec) -> Vec:
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec) -> Vec:
        return self + (-other)

    def norm1(self) -> T:
        return abs(self.x) + abs(self.y)

    def norm2(self) -> T:
        return self.x ** 2 + self.y ** 2

    def reduce(self) -> Vec:
        d = math.gcd(self.x, self.y)
        return Vec(self.x // d, self.y // d)

    def azimuth(self) -> float:
        return math.atan2(self.x, self.y)

    def turn(self, command: TurnCommand) -> Vec:
        angle = TURN_ANGLES.get(command, command)
        if not isinstance(angle, int):
            raise TypeError(f"unknown value type: {command!r}")
        if angle % 360 == 0:
            return self
        if angle % 360 == 90:
            return Vec(-self.y, self.x)
        if angle % 360 == 180:
            return Vec(-self.x, -self.y)
        if angle % 360 == 270:
            return Vec(self.y, -self.x)
        raise ValueError(f"unknown turning command: {command!r}")
