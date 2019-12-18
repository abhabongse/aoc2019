"""
Day 9: Sensor Boost
"""
import asyncio
import os
from typing import List

import uvloop

from solves.day09.machine import Execution, Program

this_dir = os.path.dirname(os.path.abspath(__file__))
boost_filename = os.path.join(this_dir, "boost.txt")


def read_boost_program(filename: str) -> Program:
    with open(filename) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


################
# For part one #
################

class CustomExecution(Execution):
    boost_mode: int
    count: int
    outputs: List[int]

    def __init__(self, program: Program, boost_mode: int):
        super().__init__(program)
        self.boost_mode = boost_mode
        self.count = 0
        self.outputs = []

    async def input(self) -> int:
        self.count += 1
        if self.count == 2:
            print("Warning: input sent more than once")
        return self.boost_mode

    async def output(self, value: int) -> None:
        await super().output(value)
        self.outputs.append(value)


async def solve_part_one():
    boost_program = read_boost_program(boost_filename)
    executor = CustomExecution(boost_program, 1)
    await executor.run()
    print(executor.outputs[-1])


async def solve_part_two():
    boost_program = read_boost_program(boost_filename)
    executor = CustomExecution(boost_program, 2)
    await executor.run()
    print(executor.outputs[-1])


################
# Main program #
################

async def main():
    await solve_part_one()
    await solve_part_two()


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
