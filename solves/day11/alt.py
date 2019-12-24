"""
Day 11: Space Police
"""
import asyncio
import os
from collections import defaultdict
from typing import Dict, NamedTuple

import uvloop

from solves.day09.machine import PipeIntcodeMachine, Program


####################
# Data definitions #
####################

class Vector2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)


##################
# Main functions #
##################

class Drawer:
    canvas: Dict[Vector2D, int]
    loc: Vector2D
    heading: int

    heading_map = {
        0: Vector2D(0, 1),
        1: Vector2D(1, 0),
        2: Vector2D(0, -1),
        3: Vector2D(-1, 0),
    }

    def __init__(self, program: Program, starting_panel: int = 0):
        self.machine = PipeIntcodeMachine(program)
        self.canvas = defaultdict(int)
        self.loc = Vector2D(0, 0)
        self.canvas[self.loc] = starting_panel
        self.heading = 0

    async def draw(self):
        loop_task = asyncio.create_task(self.loop())
        await self.machine.run()
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

    async def loop(self):
        while True:
            await self.step()
            await asyncio.sleep(0.001)

    async def step(self):
        old_value = self.canvas[self.loc]
        await self.machine.input_values.put(old_value)

        new_value = await self.machine.output_values.get()
        self.canvas[self.loc] = new_value

        turn = await self.machine.output_values.get()
        self.heading = (self.heading + 2 * turn - 1) % 4
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


async def p1_false_paint(painter_program: Program):
    drawer = Drawer(painter_program)
    await drawer.draw()
    result = len(drawer.canvas)
    print(f"Painted panels: {result}")


async def p2_true_paint(painter_program: Program):
    drawer = Drawer(painter_program, starting_panel=1)
    await drawer.draw()
    paint_pixels(drawer.canvas)


################
# Main program #
################

async def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    painter_opcode_filename = os.path.join(this_dir, "painter.txt")
    painter_program = read_painter_program(painter_opcode_filename)

    await p1_false_paint(painter_program)
    await p2_true_paint(painter_program)


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
