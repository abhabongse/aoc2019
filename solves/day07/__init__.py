"""
Day 7: Amplification Circuit
"""
import asyncio
import itertools
import os

import uvloop

from solves.day07.machine import Execution

this_dir = os.path.dirname(os.path.abspath(__file__))
amplifier_file = os.path.join(this_dir, "amplifier.txt")


def read_amplifier_program(file):
    with open(file) as fobj:
        return tuple(int(token) for token in fobj.read().split(","))


############
# Part one #
############

class AmplifierExec(Execution):
    def __init__(self, program, phase, input_signal):
        super().__init__(program)
        self.phase = phase
        self.input_signal = input_signal
        self.output_signal = None
        self.counter = 0

    async def input(self) -> int:
        if self.counter == 0:
            self.counter += 1
            return self.phase
        elif self.counter == 1:
            self.counter += 1
            return self.input_signal
        else:
            raise RuntimeError

    async def output(self, value: int) -> None:
        self.output_signal = value


async def test_thruster(amplifier_program, phase_setting):
    current_signal = 0
    for phase in phase_setting:
        executor = AmplifierExec(amplifier_program, phase, current_signal)
        await executor.run()
        current_signal = executor.output_signal
    return current_signal


async def solve_part_one():
    amplifier_program = read_amplifier_program(amplifier_file)
    signals = [
        await test_thruster(amplifier_program, phase_setting)
        for phase_setting in itertools.permutations([0, 1, 2, 3, 4])
    ]
    print(max(signals))


############
# Part two #
############


################
# Main program #
################

async def main():
    await solve_part_one()


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
