from common import driver_code
from util import distance, construct_dist_matrix, calculate_total_distance
import sys


def solve(cities):
    '''
    2-opt solution
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


# -------------functions used to find cross and resolve them iteratively-------------

def is_cross(a1, a2, b1, b2) -> bool:
    '''
    detect if given edge forms cross 
    args: 
        a1, a2: vertex of edge a; b1, b2: vertex of edge b
    return
        if is cross, return true
    check if total distance after swapping((a1,b1), (a2,b2)) is smaller
    if is smaller, means the current should be swapped
    '''
    len_delta = - distance(a1, a2) - distance(b1, b2) + distance(a1, b1) + distance(a2, b2)
    return len_delta < 0


def two_opt_swap(i, j, tour):
    '''
    perform 2-opt swap
    args: edge a's start, edge b's start, origin tour
    returns: swapped tour
    in order to keep the path valid, any root between the cross(i+1(included) to j+1(excluded)) should be reversed
    '''
    tour[i+1:j+1] = list(reversed(tour[i+1:j+1]))
    return tour


def find_single_cross(cities, tour) -> tuple[int]:
    '''
    loop through all combinations of edges and check if they should be swapped
    args: 
        cities: the formattted coordinate of each vertex
        tour: the order(indexes of coordinates in cities list) of visit
    return: cross: (edge_a_start, edge_a_start)
    return the first cross found
    '''

    # n-1: number of edges
    n = len(tour)

    # total edges to check: combination len(cities)*(len(cities)-1)/2
    # i, j: the idx in tours(the order to visit), not the idx in cities
    for i in range(n):
        # skip current edge and next edge
        for j in range(i+2, n):

            # skip last edge that back to origin(other wise it will be detected as a cross)
            if j == n-1 and i == 0:
                continue
            edge_a_start = cities[tour[i]]
            edge_a_end = cities[tour[i+1]]
            edge_b_start = cities[tour[j]]
            edge_b_end = cities[tour[(j+1) % n]]  # the last edge's vertex will be (tour[-1], tour[1])
            if is_cross(edge_a_start, edge_a_end, edge_b_start, edge_b_end):
                return (i, j)

                # add the idx of start vertex of edge a and start vertex of edge b in order to swap

    return (-1, -1)


def find_all_cross(cities, tour) -> list[tuple[tuple[int]]]:
    '''
    currently not used in any
    args: 
        cities: the formattted coordinate of each vertex
        tour: the order(indexes of coordinates in cities list) of visit
    return: a list of all crosses: [(edge_a_start, edge_b_start)]
    '''
    crosses = []
    # n-1: number of edges
    n = len(tour)

    # total edges to check: combination len(cities)*(len(cities)-1)/2
    # i, j: the idx in tours(the order to visit), not the idx in cities
    for i in range(n):
        # skip current edge and next edge
        for j in range(i+2, n):
            # skip last edge that back to origin(other wise it will be detected as a cross)
            if j == n-1 and i == 0:
                continue
            edge_a_start = cities[tour[i]]
            # edge_a_end = tour[(i+1) % n]  # if i is n-1, j will in range (n+1, n), which won't'be executed
            edge_a_end = cities[tour[i+1]]
            edge_b_start = cities[tour[j]]
            edge_b_end = cities[tour[(j+1) % n]]  # the last edge's vertex will be (tour[-1], tour[1])
            if is_cross(edge_a_start, edge_a_end, edge_b_start, edge_b_end):
                crosses.append((i, j))
                # add the idx of start vertex of edge a and start vertex of edge b in order to swap

    return crosses


def iterative_resolve_cross(cities, tour):
    '''
    find single cross and resolve it, until no cross remind
    '''
    current_distance = calculate_total_distance(cities, tour)
    MAXIMUM_ITERATION = 10000
    i = 0
    while i < MAXIMUM_ITERATION:
        i, j = find_single_cross(cities, tour)
        if i == -1 and j == -1:
            # if there's no remainning cross to swap
            break
        tour = two_opt_swap(i, j, tour)
        current_distance = calculate_total_distance(cities, tour)
        print(current_distance)
        i += 1
    return tour


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    # driver_code('a', solve, False)
    driver_code('a', solve, True)
