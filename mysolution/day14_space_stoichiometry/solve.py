from __future__ import annotations

import collections
import math
import os
import re
from collections.abc import Callable, Sequence
from graphlib import TopologicalSorter  # noqa: I
from typing import NamedTuple, TypeVar  # noqa: I

T = TypeVar('T')

CHEMICAL_RE = re.compile(r'\s*(?P<amount>\d+)\s*(?P<name>\w+)\s*')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    formulae = read_input_file(input_file)

    # Part 1
    required_amounts = required_amounts_per_target(formulae, target=Chemical('FUEL', 1))
    p1_answer = required_amounts['ORE']
    print(p1_answer)

    # Part 2
    p2_answer = fuels_from_ores(formulae, ore_amount=1_000_000_000_000)
    print(p2_answer)


class Chemical(NamedTuple):
    name: str
    amount: int

    @classmethod
    def from_raw(cls, raw: str) -> Chemical:
        data = CHEMICAL_RE.fullmatch(raw).groupdict()
        return Chemical(data['name'], int(data['amount']))


class Formula(NamedTuple):
    reactants: list[Chemical]
    product: Chemical

    @classmethod
    def from_raw(cls, raw: str) -> Formula:
        reactants, product = raw.split('=>')
        product = Chemical.from_raw(product)
        reactants = [Chemical.from_raw(r) for r in reactants.split(',')]
        return Formula(reactants, product)


def fuels_from_ores(formulae: Sequence[Formula], ore_amount: int) -> int:
    def enough_ores(fuel_amount: int) -> bool:
        required_amounts = required_amounts_per_target(formulae, target=Chemical('FUEL', fuel_amount))
        return required_amounts['ORE'] <= ore_amount

    index = binary_search_max_satisfied(range(ore_amount), pred=enough_ores)
    return range(ore_amount)[index]


def required_amounts_per_target(formulae: Sequence[Formula], target: Chemical) -> dict[str, int]:
    dependencies = collections.defaultdict(list)
    for reactants, product in formulae:
        for r in reactants:
            dependencies[r.name].append(product.name)
    sorter = TopologicalSorter(dependencies)

    formulae_by_product_name = {f.product.name: f for f in formulae}
    accm_required_amounts = collections.defaultdict(int, {target.name: target.amount})

    for product_name in sorter.static_order():
        try:
            formula = formulae_by_product_name[product_name]
        except KeyError:
            continue
        reps = math.ceil(accm_required_amounts[product_name] / formula.product.amount)
        for reactant_name, required_amount_per_rep in formula.reactants:
            accm_required_amounts[reactant_name] += required_amount_per_rep * reps

    return accm_required_amounts


def binary_search_max_satisfied(values: Sequence[T], pred: Callable[[T], bool], lo: int = 0,
                                hi: int = None) -> T:
    """
    Locates the index within the given sequence of values using binary search
    such that the following assertions are both true (assuming such index exists):
    - `all(pred(value) for value in candidates[:index])`
    - `all(not pred(value) for value in candidates[index:])`
    """
    hi = len(values) if hi is None else hi
    while lo < hi:
        mid = math.ceil((lo + hi) / 2)
        if pred(values[mid]):
            lo = mid
        else:
            hi = mid - 1
    return hi


def read_input_file(filename: str) -> list[Formula]:
    """
    Extracts a list of chemical formulae.
    """
    with open(filename) as fobj:
        formulae = [Formula.from_raw(line) for line in fobj]
    return formulae


if __name__ == '__main__':
    main()
