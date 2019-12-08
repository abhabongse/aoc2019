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
        await asyncio.sleep(0.001)
        if self.counter == 0:
            self.counter += 1
            return self.phase
        elif self.counter == 1:
            self.counter += 1
            return self.input_signal
        else:
            raise RuntimeError

    async def output(self, value: int) -> None:
        await asyncio.sleep(0.001)
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

class WiredAmplifierExec(Execution):
    def __init__(self, program, phase, input_queue, output_queue, key):
        super().__init__(program)
        self.phase = phase
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.key = key
        self.last_output = False
        self.counter = 0

    async def input(self) -> int:
        await asyncio.sleep(0.001)
        if self.counter == 0:
            self.counter += 1
            return self.phase
        else:
            value = await self.input_queue.get()
            # print(f"{self.key} receives {value}")
            return value

    async def output(self, value: int) -> None:
        await asyncio.sleep(0.001)
        self.last_output = value
        # print(f"{self.key} returns {value}")
        await self.output_queue.put(value)


async def test_wired_thruster(amplifier_program, phase_setting):
    n = len(phase_setting)

    # Prepare signal queues between amplifiers
    # Note: amplifier executors[i] reads from queues[i] and writes to queues[i+1]
    queues = [asyncio.Queue(1) for _ in range(n)]
    await queues[0].put(0)
    executors = [
        WiredAmplifierExec(amplifier_program, phase,
                           queues[index], queues[(index + 1) % n], index)
        for index, phase in enumerate(phase_setting)
    ]

    # Fire all executors except last
    tasks = [
        asyncio.create_task(executor.run())
        for executor in executors[:-1]
    ]
    # Wait until the last executor finishes
    await executors[-1].run()
    # Cancel all remaining tasks
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Extract the last output signal from the last executor
    value = executors[-1].last_output
    return value


async def solve_part_two():
    amplifier_program = read_amplifier_program(amplifier_file)
    signals = [
        await test_wired_thruster(amplifier_program, phase_setting)
        for phase_setting in itertools.permutations([5, 6, 7, 8, 9])
    ]
    print(max(signals))


################
# Main program #
################

async def main():
    await solve_part_one()
    await solve_part_two()


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
