"""
Day 6: Universal Orbit Map
"""
import math
import os
from collections import defaultdict, deque
from typing import Dict, List, Tuple

import numpy as np
from tqdm import trange

AdjList = Dict[str, List[str]]


def read_orbits(filename: str) -> List[Tuple[str, str]]:
    with open(filename) as fobj:
        return [
            tuple(line.strip().split(")"))
            for line in fobj
        ]


################
# For part one #
################

def orbits_to_transitive_mat(orbit_pairs: List[Tuple[str, str]]) -> np.ndarray:
    # Collection of unique bodies
    bodies = {
        body
        for orbit_pair in orbit_pairs
        for body in orbit_pair
    }
    # Mapping from body to a unique integer
    bodies = {
        body: index
        for index, body in enumerate(sorted(bodies))
    }
    mat = np.identity(len(bodies), dtype='int8')
    for center, surround in orbit_pairs:
        mat[bodies[center], bodies[surround]] = 1
    return mat


def mul_bool(fst: np.ndarray, snd: np.ndarray) -> np.ndarray:
    """
    Boolean multiplication.
    """
    return np.where(fst @ snd, 1, 0).astype('int8')


def transitive_closure(mat: np.ndarray) -> np.ndarray:
    # Number of times required to do matrix multiplication
    times = int(math.log2(mat.shape[0])) + 1
    res = mat
    for _ in trange(times + 2):
        res = mul_bool(res, res)
    return res


def p1_count_reachable_pairs(orbit_pairs: List[Tuple[str, str]]):
    """
    Find the reachable pair of vertices using Adjacency Matrix
    with Transitive Closure finding through multiplication.
    """
    mat = orbits_to_transitive_mat(orbit_pairs)
    mat = transitive_closure(mat)
    result = np.sum(mat) - mat.shape[0]
    print(f"Part one: {result=}")


################
# For part two #
################

def orbits_to_adjacency_list(orbit_pairs: List[Tuple[str, str]]) -> AdjList:
    adjlist = defaultdict(list)
    for fst, snd in orbit_pairs:
        adjlist[fst].append(snd)
        adjlist[snd].append(fst)
    return adjlist


def bfs(adjlist: AdjList, src: str, dest: str) -> int:
    queue = deque([(src, 0)])
    distances = {}
    while queue:
        curr, dist = queue.popleft()
        if curr in distances:
            continue
        distances[curr] = dist
        for next in adjlist[curr]:
            queue.append((next, dist + 1))
    return distances[dest]


def p2_path_length(orbit_pairs: List[Tuple[str, str]]):
    """
    Use Breadth-First Search to find distance between two vertices
    of an unweighted graph.
    """
    adjlist = orbits_to_adjacency_list(orbit_pairs)
    result = bfs(adjlist, 'YOU', 'SAN') - 2  # remove two steps
    print(f"Part two: {result=}")


################
# Main program #
################

if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    orbits_filename = os.path.join(this_dir, "orbits.txt")
    orbit_pairs = read_orbits(orbits_filename)

    p1_count_reachable_pairs(orbit_pairs)
    p2_path_length(orbit_pairs)
