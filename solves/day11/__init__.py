"""
Day 11: Space Police
"""
import asyncio
import os
from collections import defaultdict
from typing import Dict, NamedTuple

import uvloop

from solves.day09.machine import Execution, Program

this_dir = os.path.dirname(os.path.abspath(__file__))
painter_filename = os.path.join(this_dir, "painter.txt")


class Vector2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)


class PainterExecution(Execution):
    canvas: Dict[Vector2D, int]
    loc: Vector2D
    heading: int
    output_count: int

    heading_map = {
        0: Vector2D(0, 1),
        1: Vector2D(1, 0),
        2: Vector2D(0, -1),
        3: Vector2D(-1, 0),
    }

    def __init__(self, program: Program, starting_panel: int = 0):
        super().__init__(program)
        self.canvas = defaultdict(int)
        self.loc = Vector2D(0, 0)
        self.canvas[self.loc] = starting_panel
        self.heading = 0
        self.output_count = 0

    async def input(self) -> int:
        return self.canvas[self.loc]

    async def output(self, value: int) -> None:
        if self.output_count % 2 == 0:
            await self.first_output(value)
        else:
            await self.second_output(value)
        self.output_count += 1

    async def first_output(self, value: int) -> None:
        self.canvas[self.loc] = value

    async def second_output(self, value: int) -> None:
        self.heading = (self.heading + 2 * value - 1) % 4
        self.loc += self.heading_map[self.heading]


def read_painter_program(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


def paint_pixels(canvas: Dict[Vector2D, int]):
    black_pixels = [
        pixel
        for pixel, value in canvas.items()
        if value
    ]
    offset = Vector2D(
        x=min(pixel.x for pixel in black_pixels),
        y=min(pixel.y for pixel in black_pixels),
    )
    black_pixels = [pixel - offset for pixel in black_pixels]
    width = max(pixel.x for pixel in black_pixels) + 1
    height = max(pixel.y for pixel in black_pixels) + 1

    board = [[' ' for _ in range(width)] for _ in range(height)]
    for pixel in black_pixels:
        board[pixel.y][pixel.x] = '#'
    print('\n'.join(''.join(line) for line in reversed(board)))


async def solve_part_one():
    painter_program = read_painter_program(painter_filename)
    executor = PainterExecution(painter_program)
    await executor.run()
    result = len(executor.canvas)
    print(f"Painted panels: {result}")


async def solve_part_two():
    painter_program = read_painter_program(painter_filename)
    executor = PainterExecution(painter_program, starting_panel=1)
    await executor.run()
    paint_pixels(executor.canvas)


################
# Main program #
################

async def main():
    await solve_part_one()
    await solve_part_two()


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
