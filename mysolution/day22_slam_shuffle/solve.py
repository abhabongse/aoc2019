from __future__ import annotations

import functools
import itertools
import os
import re
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, TypeVar

T = TypeVar('T')


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    shuffles = read_input_file(input_file)

    # Part 1
    deck = functools.reduce(lambda d, s: s.shuffle_seq(d), shuffles, range(10007))
    p1_answer = deck.index(2019)
    print(p1_answer)

    # Part 2
    starting_deck = CyclicDeck(119315717514047)
    deck = functools.reduce(lambda d, s: s.shuffle_cyclic_deck(d), shuffles, starting_deck)
    deck = deck.pow(101741582076661)
    p2_answer = deck[2020]
    print(p2_answer)


@dataclass(frozen=True)
class CyclicDeck(Sequence[int]):
    size: int
    start: int = 0
    step: int = 1

    def __getitem__(self, index: int) -> int:
        if not isinstance(index, int):
            raise TypeError
        if not -self.size <= index < self.size:
            raise IndexError
        return (self.start + self.step * index) % self.size

    def __len__(self) -> int:
        return self.size

    def index(self, value: int, start: int = None, stop: int = None) -> int:
        index = ((value - self.start) * pow(self.step, -1, self.size)) % self.size
        if not -self.size <= index < self.size:
            raise ValueError
        return index

    def __matmul__(self, other: CyclicDeck) -> CyclicDeck:
        fst = self[other[0]]
        snd = self[other[1]]
        return CyclicDeck(self.size, fst, (snd - fst) % self.size)

    def invert(self):
        fst = self.index(0)
        snd = self.index(1)
        return CyclicDeck(self.size, fst, (snd - fst) % self.size)

    def pow(self, exp: int) -> CyclicDeck:
        if exp < 0:
            return self.invert().pow(-exp)

        accm = CyclicDeck(self.size)
        powers = self
        while exp:
            if exp % 2 == 1:
                accm = accm @ powers
            powers = powers @ powers
            exp //= 2
        return accm


class CardShuffle(metaclass=ABCMeta):
    """
    Represents a card shuffling process.
    """
    pattern: ClassVar[re.Pattern]
    subclasses: ClassVar[list[type[CardShuffle]]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @classmethod
    def from_raw(cls, raw: str):
        for subclass in cls.subclasses:
            if matchobj := subclass.pattern.fullmatch(raw.strip()):
                return subclass.parse(**matchobj.groupdict())
        raise ValueError

    @classmethod
    def parse(cls: type[T], **kwargs) -> T:
        """
        Parses the captured regular expression pattern into instance.
        """
        return cls()

    @abstractmethod
    def shuffle_seq(self, cards: Sequence[int]) -> list[int]:
        """
        Shuffles the given deck of cards into a new ordering.
        """
        raise NotImplementedError

    @abstractmethod
    def shuffle_cyclic_deck(self, deck: CyclicDeck) -> CyclicDeck:
        """
        Shuffles the given cyclic deck object.
        """
        raise NotImplementedError


@dataclass
class Reverse(CardShuffle):
    pattern = re.compile(r'deal into new stack')

    def shuffle_seq(self, cards: Sequence[int]) -> list[int]:
        return list(reversed(cards))

    def shuffle_cyclic_deck(self, deck: CyclicDeck) -> CyclicDeck:
        return CyclicDeck(deck.size, deck[-1], -deck.step)


@dataclass
class Cut(CardShuffle):
    pattern = re.compile(r'cut (?P<n>-?\d+)')
    n: int

    @classmethod
    def parse(cls, *, n: str, **kwargs) -> Cut:
        return Cut(int(n))

    def shuffle_seq(self, cards: Sequence[int]) -> list[int]:
        return list(itertools.chain(cards[self.n:], cards[:self.n]))

    def shuffle_cyclic_deck(self, deck: CyclicDeck) -> CyclicDeck:
        return CyclicDeck(deck.size, deck[self.n], deck.step)


@dataclass
class Increment(CardShuffle):
    pattern = re.compile(r'deal with increment (?P<n>\d+)')
    n: int

    @classmethod
    def parse(cls, *, n: str, **kwargs) -> Increment:
        return Increment(int(n))

    def shuffle_seq(self, cards: Sequence[int]) -> list[int]:
        size = len(cards)
        index_lookup = {card: (index * self.n) % size for index, card in enumerate(cards)}
        return sorted(cards, key=lambda card: index_lookup[card])

    def shuffle_cyclic_deck(self, deck: CyclicDeck) -> CyclicDeck:
        new_step = ((deck[1] - deck[0]) * pow(self.n, -1, deck.size)) % deck.size
        return CyclicDeck(deck.size, deck.start, new_step)


def read_input_file(filename: str) -> list[CardShuffle]:
    """
    Extracts a list of card shuffling processes.
    """
    with open(filename) as fobj:
        shuffles = [CardShuffle.from_raw(line) for line in fobj]
    return shuffles


if __name__ == '__main__':
    main()
