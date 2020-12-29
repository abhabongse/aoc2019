from __future__ import annotations

import os
import sys
from typing import TextIO

import numpy as np


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    digits = read_input_file(input_file)

    # Part 1
    layers = split_layers(digits, width=25, height=6)
    p1_answer = layers_checksum(layers)
    print(p1_answer)

    # Part 2
    image = decode_image(layers)
    print_image(image)


def split_layers(digits: str, width: int, height: int) -> np.ndarray:
    """
    Deserializes an image into multiple layers of the given width and height.
    """
    return np.reshape([int(d) for d in digits], (-1, height, width))


def layers_checksum(layers: np.ndarray) -> bool:
    """
    Computes the checksum of the received image layers.
    """
    zero_counts = (layers == 0).sum(axis=(1, 2))
    considered_layer = layers[np.argmin(zero_counts)]
    one_count = (considered_layer == 1).sum()
    two_count = (considered_layer == 2).sum()
    return one_count * two_count


def decode_image(layers: np.ndarray) -> np.ndarray:
    """
    Decodes the image by applying layer masks on top of one another.
    """
    canvas = layers[-1]
    for layer in layers[::-1]:
        canvas = np.where(layer < 2, layer, canvas).astype('int8')
    return canvas


def print_image(image: np.ndarray, stream: TextIO = sys.stdout):
    """
    Prints the image to the given stream.
    """
    for line in image:
        buffer = ''.join('#' if char else ' ' for char in line)
        print(buffer, file=stream)


def read_input_file(filename: str) -> str:
    """
    Extracts a serialized list of digits for a multi-layer image.
    """
    with open(filename) as fobj:
        digits = fobj.read().strip()
    return digits


if __name__ == '__main__':
    main()
