"""
Day 9: Sensor Boost
"""
import asyncio
import os
from typing import List

import uvloop

from legacy.day09.machine import IntcodeMachine, Program


class BoostMachine(IntcodeMachine):
    boost_mode: int
    count: int
    outputs: List[int]

    def __init__(self, program: Program, boost_mode: int):
        super().__init__(program)
        self.boost_mode = boost_mode
        self.count = 0
        self.outputs = []

    async def get_input(self) -> int:
        self.count += 1
        if self.count == 2:
            print("Warning: input sent more than once")
        return self.boost_mode

    async def set_output(self, value: int) -> None:
        self.outputs.append(value)


def read_boost_program(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


async def p1_normal_mode(boost_program: Program):
    executor = BoostMachine(boost_program, 1)
    await executor.run()
    output = executor.outputs[-1]
    print(f"Part one: {output=}")


async def p2_feedback_mode(boost_program: Program):
    executor = BoostMachine(boost_program, 2)
    await executor.run()
    output = executor.outputs[-1]
    print(f"Part two: {output=}")


################
# Main program #
################

async def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    boost_opcode_filename = os.path.join(this_dir, "boost.txt")
    boost_program = read_boost_program(boost_opcode_filename)

    await p1_normal_mode(boost_program)
    await p2_feedback_mode(boost_program)


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
