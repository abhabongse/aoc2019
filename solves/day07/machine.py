"""
Intcode computer.
"""
import asyncio
import inspect
from typing import Callable, Iterable, List

Program = Iterable[int]
Memory = List[int]
InputFunc = Callable[[], int]
OutputFunc = Callable[[int], None]


class ProgramStopped(Exception):
    pass


class IntcodeMachine:
    memory: Memory
    pc: int

    def __init__(self, program: Program):
        self.memory = list(program)
        self.pc = 0

    async def execute(self, execution: 'Execution'):
        instr = self.memory[self.pc]

        # Obtain method from current instruction
        opcode = f'{instr % 100:02}'
        method = getattr(self, f'execute_{opcode}')
        sig = inspect.signature(method)
        nargs = sum(param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
                    for param in sig.parameters.values())

        # Compute parameter modes from current instruction
        param_modes = []
        instr_value = instr // 100
        for pos in range(nargs):
            param_modes.append(instr_value % 10)
            instr_value //= 10

        # Obtain arguments
        args = [self.memory[self.pc + 1 + pos]
                for pos in range(nargs)]

        # Fire and move on
        await method(*args, modes=param_modes, execution=execution)

    def get_value(self, param, mode):
        if mode == 0:
            return self.memory[param]
        elif mode == 1:
            return param
        else:
            raise RuntimeError(f"unknown mode: {mode!r}")

    def set_value(self, param, mode, value):
        if mode == 0:
            self.memory[param] = value
        elif mode == 1:
            raise RuntimeError(f"invalid mode: {mode!r}")
        else:
            raise RuntimeError(f"unknown mode: {mode!r}")

    async def execute_01(self, fst_param, snd_param, res_param, *, modes, **_):
        """
        Opcode 1: Compute addition: result = fst + snd.
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = fst_value + snd_value
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    async def execute_02(self, fst_param, snd_param, res_param, *, modes, **_):
        """
        Opcode 2: Compute multiplication: result = fst * snd.
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = fst_value * snd_value
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    async def execute_03(self, target_param, *, modes, execution, **_):
        """
        Opcode 3: Save input integer to target
        """
        value = await execution.input()
        self.set_value(target_param, modes[0], value)
        self.pc += 2

    async def execute_04(self, source_param, *, modes, execution, **_):
        """
        Opcode 4: Output integer from source location
        """
        value = self.get_value(source_param, modes[0])
        await execution.output(value)
        self.pc += 2

    async def execute_05(self, cond_param, pos_param, *, modes, **_):
        """
        Opcode 5: JUMP-IF-TRUE
        If conditional param is non-zero, next jump pc to given position.
        """
        cond_value = self.get_value(cond_param, modes[0])
        pos_value = self.get_value(pos_param, modes[1])
        self.pc = pos_value if cond_value else self.pc + 3

    async def execute_06(self, cond_param, pos_param, *, modes, **_):
        """
        Opcode 5: JUMP-IF-FALSE
        If conditional param is zero, next jump pc to given position.
        """
        cond_value = self.get_value(cond_param, modes[0])
        pos_value = self.get_value(pos_param, modes[1])
        self.pc = pos_value if not cond_value else self.pc + 3

    async def execute_07(self, fst_param, snd_param, res_param, *, modes, **_):
        """
        Opcode 7: LESS THAN
        If first param is LESS THAN second param, set result param to 1 (or else to 0).
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = 1 if fst_value < snd_value else 0
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    async def execute_08(self, fst_param, snd_param, res_param, *, modes, **_):
        """
        Opcode 8: EQUALS
        If first param is EQUAL TO second param, set result param to 1 (or else to 0).
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = 1 if fst_value == snd_value else 0
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    async def execute_99(self, **kwargs):
        raise ProgramStopped


class Execution:
    def __init__(self, program: Program):
        self.machine = IntcodeMachine(program)

    async def run(self):
        try:
            while True:
                await self.machine.execute(self)
        except ProgramStopped:
            pass

    async def input(self) -> int:
        await asyncio.sleep(0.001)
        return int(input("Enter an input integer:"))

    async def output(self, value: int) -> None:
        print(f"Integer output: {value!r}")
