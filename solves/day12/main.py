"""
Day 12: The N-Body Problem
"""
import os
import re
from typing import List, NamedTuple


####################
# Data definitions #
####################

class Vector3D(NamedTuple):
    x: int
    y: int
    z: int

    vector_re = re.compile(
        r"<\s*"
        r"x\s*=\s*(?P<x>-?[0-9]+)"
        r"\s*,\s*"
        r"y\s*=\s*(?P<y>-?[0-9]+)"
        r"\s*,\s*"
        r"z\s*=\s*(?P<z>-?[0-9]+)"
        r"\s*>",
    )

    @classmethod
    def zero(self) -> 'Vector3D':
        return Vector3D(0, 0, 0)

    @classmethod
    def from_string(cls, value: str) -> 'Vector3D':
        if matchobj := cls.vector_re.fullmatch(value.strip()):
            data = matchobj.groupdict()
            data = {key: int(value) for key, value in data.items()}
            return Vector3D(**data)
        raise ValueError(f"unmatched string: {value!r}")


class Body(NamedTuple):
    pos: Vector3D
    vel: Vector3D


##################
# Main functions #
##################

def read_positions(filename: str) -> List[Vector3D]:
    with open(filename) as fobj:
        return [
            Vector3D.from_string(line)
            for line in fobj
        ]


def solve_part_one(init_positions: List[Vector3D]):
    init_state = {
        index: Body(pos=pos, vel=Vector3D.zero())
        for index, pos in enumerate(init_positions)
    }
    print(init_state)


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    positions_filename = os.path.join(this_dir, "positions.txt")
    positions = read_positions(positions_filename)

    solve_part_one(positions)
