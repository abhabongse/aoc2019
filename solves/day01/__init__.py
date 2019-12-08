"""
Day 1: The Tyranny of the Rocket Equation
"""
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
masses_file = os.path.join(this_dir, "masses.txt")


############
# Part One #
############

def solve_part_one():
    masses = read_masses(masses_file)
    print(sum(mass_to_fuel(mass) for mass in masses))


def read_masses(file):
    with open(file) as fobj:
        return [int(line) for line in fobj]


def mass_to_fuel(mass):
    return mass // 3 - 2


############
# Part Two #
############

def solve_part_two():
    masses = read_masses(masses_file)
    print(sum(mass_to_compound_fuel(mass) for mass in masses))


def mass_to_compound_fuel(mass):
    cumulative_fuel = 0
    fuel = mass_to_fuel(mass)
    while fuel > 0:
        cumulative_fuel += fuel
        fuel = mass_to_fuel(fuel)
    return cumulative_fuel


if __name__ == '__main__':
    solve_part_one()
    solve_part_two()
