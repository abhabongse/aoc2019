from __future__ import annotations

import os

import numpy as np


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(this_dir, 'input.txt')
    digits = read_input_file(input_file)

    # Part 1
    layers = split_layers(digits, width=25, height=6)
    p1_answer = validate_layers(layers)
    print(p1_answer)

    # Part 2
    image = decode_image(layers)
    paint_image(image)


def split_layers(digits: str, width: int, height: int) -> np.ndarray:
    return np.reshape([int(d) for d in digits], (-1, height, width))


def validate_layers(layers: np.ndarray) -> bool:
    zero_counts = (layers == 0).sum(axis=(1, 2))
    considered_layer = layers[np.argmin(zero_counts)]
    one_count = (considered_layer == 1).sum()
    two_count = (considered_layer == 2).sum()
    return one_count * two_count


def decode_image(layers: np.ndarray) -> np.ndarray:
    canvas = layers[-1]
    for layer in layers[::-1]:
        canvas = np.where(layer < 2, layer, canvas).astype('int8')
    return canvas


def paint_image(image: np.ndarray):
    for line in image:
        buffer = ''.join('#' if char else ' ' for char in line)
        print(buffer)


def read_input_file(filename: str) -> str:
    """
    Extracts a serialized list of digits for a multi-layer image.
    """
    with open(filename) as fobj:
        digits = fobj.read().strip()
    return digits


if __name__ == '__main__':
    main()
