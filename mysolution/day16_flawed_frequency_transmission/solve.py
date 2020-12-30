from __future__ import annotations

import functools
import itertools
import multiprocessing as mp
import os
from collections.abc import Iterator, Sequence
from typing import TypeVar

import more_itertools
from tqdm import tqdm, trange

T = TypeVar('T')

# Read-only data shared across multiple processes
_N: int
_PREFIX_SUM: list[int]


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    starting_signal = read_input_file(input_file)
    offset = functools.reduce(lambda x, y: x * 10 + y, starting_signal[:7])

    # Part 1
    signal = starting_signal
    for _ in trange(100, desc="Phase", leave=False):
        signal = apply_fft(signal)
    p1_answer = ''.join(str(d) for d in signal[:8])
    print(p1_answer)

    # Part 2
    signal = starting_signal * 10000
    for _ in trange(100, desc="Phase", leave=False):
        signal = apply_fft(signal)
    p2_answer = ''.join(str(d) for d in signal[offset:offset + 8])
    print(p2_answer)


def apply_fft(signal: Sequence[int]) -> list[int]:
    """
    Applies Flawed Frequency Transmission (FFT) algorithm to an input signal.
    Subtasks are divided and run in parallel through multiprocessing pool.

    It exploits copy-on-write behavior of read-only, globally shared data
    to distribute the pre-computed `_N` and `_PREFIX_SUM`.
    Therefore, this function can be called only by a single main process.
    """
    # Setup shared read-only data
    global _N, _PREFIX_SUM
    _N = len(signal)
    _PREFIX_SUM = list(itertools.accumulate(signal, initial=0))

    # Shuffling to make sure that tasks are evenly distributed
    cpu_count = mp.cpu_count()
    shuffled_repeats = tqdm(forward_pile_shuffle(range(1, 1 + _N), cpu_count),
                            desc="Repeat", total=_N, leave=False)
    with mp.Pool(cpu_count) as pool:
        new_shuffled_signal = pool.map(_compute_digit, shuffled_repeats)

    new_unshuffled_signal = list(reverse_pile_shuffle(new_shuffled_signal, cpu_count))
    return new_unshuffled_signal


def _compute_digit(pattern_repeat: int) -> int:
    accm = 0
    for offset, sign in zip(range(-1, _N, 2 * pattern_repeat), itertools.cycle([+1, -1])):
        lo = min(offset + pattern_repeat, _N)
        hi = min(offset + 2 * pattern_repeat, _N)
        accm += sign * (_PREFIX_SUM[hi] - _PREFIX_SUM[lo])
    return last_digit(accm)


def forward_pile_shuffle(cards: Sequence[T], piles: int) -> Iterator[T]:
    """
    Pile-shuffles the cards (representing a sequence of values):
    distributing cards in round robin fashion for the given number of piles
    then concatenate them back in the same order.
    >>> list(forward_pile_shuffle(range(11), 3))
    [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8]
    """
    n = len(cards)
    for offset in range(piles):
        for index in range(offset, n, piles):
            yield cards[index]


def reverse_pile_shuffle(cards: Sequence[T], piles: int) -> Iterator[T]:
    """
    Inverses the pile-shuffle operation.
    >>> list(reverse_pile_shuffle([0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8], 3))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> list(reverse_pile_shuffle(range(11), 3))
    """
    n = len(cards)
    pile_size, overflow = divmod(n, piles)
    pile_groups = []

    index = 0
    for _ in range(overflow):
        pile_groups.append(cards[index: index + pile_size + 1])
        index += pile_size + 1
    for _ in range(overflow, piles):
        pile_groups.append(cards[index: index + pile_size])
        index += pile_size

    yield from more_itertools.interleave_longest(*pile_groups)


def last_digit(number: int) -> int:
    """
    Returns the last digit of the number (in absolute magnitude).
    """
    return abs(number) % 10


def read_input_file(filename: str) -> list[int]:
    """
    Extracts a signal which is a list of digits.
    """
    with open(filename) as fobj:
        signal = [int(d) for d in fobj.read().strip()]
    return signal


if __name__ == '__main__':
    main()
