"""
Intcode computer.
"""
import inspect
from typing import Callable, Iterable, List, Optional

Program = Iterable[int]
Memory = List[int]
InputFunc = Callable[[], int]
OutputFunc = Callable[[int], None]


class ProgramStopped(Exception):
    pass


class Interaction:
    """
    Interfacing object between Intcode program and the Python world.
    """

    def input(self) -> int:
        return int(input("Enter an input integer:"))

    def output(self, value: int) -> None:
        print(f"Integer output: {value!r}")


class Machine:
    """
    Intcode implementation.
    """
    memory: Memory
    pc: int
    interaction: Interaction

    def __init__(self, program: Program, interaction: Optional[Interaction] = None):
        self.memory = list(program)
        self.pc = 0
        self.interaction = interaction or Interaction()

    def run(self):
        """
        Keep running the intcode until the program terminates.
        """
        try:
            while True: self.execute()
        except ProgramStopped:
            pass

    def execute(self):
        """
        Dispatch a single instruction of the intcode program
        based on the current program counter.
        """
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
        method(*args, modes=param_modes)

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

    def execute_01(self, fst_param, snd_param, res_param, *, modes):
        """
        Opcode 1: Compute ADDITION between two params.
        result = fst + snd
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = fst_value + snd_value
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    def execute_02(self, fst_param, snd_param, res_param, *, modes):
        """
        Opcode 2: Compute MULTIPLICATION between two params.
        result = fst * snd
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = fst_value * snd_value
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    def execute_03(self, target_param, *, modes):
        """
        Opcode 3: Save INPUT integer to target.
        """
        value = self.interaction.input()
        self.set_value(target_param, modes[0], value)
        self.pc += 2

    def execute_04(self, source_param, *, modes):
        """
        Opcode 4: OUTPUT integer from source location.
        """
        value = self.get_value(source_param, modes[0])
        self.interaction.output(value)
        self.pc += 2

    def execute_05(self, cond_param, pos_param, *, modes):
        """
        Opcode 5: JUMP-IF-TRUE branching instruction.
        If conditional param is non-zero, next jump pc to given position.
        """
        cond_value = self.get_value(cond_param, modes[0])
        pos_value = self.get_value(pos_param, modes[1])
        self.pc = pos_value if cond_value else self.pc + 3

    def execute_06(self, cond_param, pos_param, *, modes):
        """
        Opcode 6: JUMP-IF-FALSE branching instruction.
        If conditional param is zero, next jump pc to given position.
        """
        cond_value = self.get_value(cond_param, modes[0])
        pos_value = self.get_value(pos_param, modes[1])
        self.pc = pos_value if not cond_value else self.pc + 3

    def execute_07(self, fst_param, snd_param, res_param, *, modes):
        """
        Opcode 7: Compute whether the first param is LESS THAN the second param.
        result = fst < snd ? 1 : 0
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = 1 if fst_value < snd_value else 0
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    def execute_08(self, fst_param, snd_param, res_param, *, modes):
        """
        Opcode 8: Compute whether the first param is EQUAL TO the second param.
        result = fst == snd ? 1 : 0
        """
        fst_value = self.get_value(fst_param, modes[0])
        snd_value = self.get_value(snd_param, modes[1])
        result = 1 if fst_value == snd_value else 0
        self.set_value(res_param, modes[2], result)
        self.pc += 4

    def execute_99(self, **kwargs):
        """
        Opcode 99: TERMINATE Intcode Program.
        """
        raise ProgramStopped
