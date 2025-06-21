import math
import numpy as np

'''
distance calculator

'''


def distance(city1, city2) -> float:
    '''
    args: coordinates(set) of 2 cities
    return: distance between 2 cities
    used in verify scores, solvers
    '''
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def construct_dist_matrix(cities: list[set[float]]) -> np.ndarray:
    '''
    args:
        a list of sets, containing corrdinates of each city
            (will be returned after reading raw csv via read file helper)
    return:
        a symmetric matrix of N*N, where N is length of cities
    '''
    N = len(cities)

    dist = np.zeros((N, N), dtype=np.float32)
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])

    return dist
