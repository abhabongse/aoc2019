"""
Day 11: Space Police
"""
import asyncio
import os
import time
from typing import Dict, List, NamedTuple, Optional

import uvloop

from legacy.day09.machine import IntcodeMachine, Program


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

class ArcadeMachine(IntcodeMachine):
    canvas: Dict[Vector2D, int]
    output_buffer: List[int]
    started: bool
    cursor: Optional[int]
    ball: Optional[int]

    num_to_char = {
        0: ' ',
        1: '#',
        2: '$',
        3: '_',
        4: 'o',
    }

    def __init__(self, program: Program, insert_coin: bool = False):
        if insert_coin:
            program = list(program)
            program[0] = 2
        super().__init__(program)
        self.canvas = {}
        self.output_buffer = []
        self.started = False
        self.cursor = None
        self.ball = None

    async def get_input(self) -> int:
        self.started = True
        if self.cursor < self.ball:
            return 1
        if self.cursor > self.ball:
            return -1
        return 0

    async def set_output(self, value: int) -> None:
        self.output_buffer.append(value)
        if len(self.output_buffer) == 3:
            self.record_tile(*self.output_buffer)
            self.output_buffer = []

    def record_tile(self, x: int, y: int, tile: int):
        loc = Vector2D(x, y)
        if loc == Vector2D(-1, 0):
            print(f"Score is: {tile}")
            return
        self.canvas[loc] = tile
        if tile == 3:  # paddle
            self.cursor = loc.x
        elif tile == 4:  # ball
            self.ball = loc.x
        # self.draw_board()

    def draw_board(self):
        if not self.started:
            return
        width = max(cell.x for cell in self.canvas.keys()) + 1
        height = max(cell.y for cell in self.canvas.keys()) + 1
        board = '\n'.join(
            ''.join(
                self.num_to_char[self.canvas[Vector2D(c, r)]]
                for c in range(width)
            )
            for r in range(height)
        )
        print(board)
        time.sleep(0.01)


def read_arcade_program(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


async def p1_count_block_tiles(arcade_program: Program):
    machine = ArcadeMachine(arcade_program)
    await machine.run()
    block_tiles = [
        loc for loc, tile in machine.canvas.items()
        if tile == 2
    ]
    print(f"Part one: {len(block_tiles)=}")


async def p2_play_game(arcade_program: Program):
    machine = ArcadeMachine(arcade_program, insert_coin=True)
    await machine.run()


################
# Main program #
################

async def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    arcade_opcode_filename = os.path.join(this_dir, "arcade.txt")
    arcade_program = read_arcade_program(arcade_opcode_filename)

    await p1_count_block_tiles(arcade_program)
    await p2_play_game(arcade_program)


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
