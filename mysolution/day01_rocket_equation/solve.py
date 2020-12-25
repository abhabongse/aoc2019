from __future__ import annotations

import os
from collections.abc import Iterator


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    masses = read_input_file(input_file)

    # Part 1
    fuels_required = sum(fuel_from_mass(m) for m in masses)
    p1_answer = fuels_required
    print(p1_answer)

    # Part 2
    fuels_required = sum(sum(compound_fuels_from_mass(m)) for m in masses)
    p2_answer = fuels_required
    print(p2_answer)


def fuel_from_mass(mass: int) -> int:
    return mass // 3 - 2


def compound_fuels_from_mass(mass: int) -> Iterator[int]:
    fuel = fuel_from_mass(mass)
    while fuel >= 0:
        yield fuel
        fuel = fuel_from_mass(fuel)


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a sequence of module masses.
    """
    with open(filename) as fobj:
        masses = [int(line) for line in fobj]
    return masses


if __name__ == '__main__':
    main()
