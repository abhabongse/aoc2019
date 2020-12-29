from __future__ import annotations

import functools
import itertools
import os
from collections.abc import Sequence

from tqdm import trange

BASE_PATTERN = [0, 1, 0, -1]


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
    Applies Flawed Frequency Transmission (FFT) algorithm
    to an input signal (as a list of digits).
    """
    n = len(signal)
    prefix_sum = list(itertools.accumulate(signal, initial=0))

    new_signal = []
    for repeat in trange(1, 1 + n, desc="Repeat", leave=False, mininterval=0.25):
        accm = 0
        for offset, sign in zip(range(-1, n, 2 * repeat), itertools.cycle([+1, -1])):
            lo = min(offset + repeat, n)
            hi = min(offset + 2 * repeat, n)
            accm += sign * (prefix_sum[hi] - prefix_sum[lo])
        new_signal.append(last_digit(accm))
    return new_signal


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
