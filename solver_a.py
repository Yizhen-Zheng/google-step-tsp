from common import driver_code
from util import distance, construct_dist_matrix, find_all_cross, find_single_cross, is_cross, two_opt_swap, iterative_resolve_cross
import sys


def solve(cities):
    '''
    args: cities: the formattted coordinate of each vertex
    return: tour: the order(indexes of coordinates in cities list) of visit
    first visit cities using greedy

    then resolve all crosses using 2 opt swap
    '''
    N = len(cities)
    dist = construct_dist_matrix(cities)
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]
    # find initial tour through greedy
    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    # 2-opt-swap
    tour = iterative_resolve_cross(cities, tour)
    return tour


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    # driver_code('a', solve, False)
    driver_code('a', solve, True)
