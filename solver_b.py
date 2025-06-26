from common import driver_code
from util import calculate_total_distance, construct_dist_matrix, distance
import sys


def solve(cities):
    '''
    args: cities: the formattted coordinate of each vertex
    return: tour: the order(indexes of coordinates in cities list) of visit
    first visit cities using greedy
    then resolve all crosses using 3 opt 
    '''
    N = len(cities)
    dist_matrix = construct_dist_matrix(cities)
    # a N*N matrix represent distance between every 2 cities, where N is total city number
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]
    # find initial tour through greedy
    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist_matrix[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city

    # 3-opt-swap
    tour = iterative_improve(tour, dist_matrix)

    print(calculate_total_distance(tour, dist_matrix))

    return tour


def iterative_improve(tour, dist_matrix):
    '''
    the main loop used to perform 3-opt for every combinations
    '''
    iter = 0
    improved = True
    current_dist = 0
    prev_dist = 0
    while improved:
        new_tour, improved = find_combination(tour, dist_matrix)
        tour = new_tour
        iter += 1
        prev_dist = current_dist
        current_dist = calculate_total_distance(tour, dist_matrix)

        if iter % 100 == 0:
            print(prev_dist, ' -> ', current_dist)

    return tour


def find_combination(tour, dist_matrix):
    '''
    args:
        tour: current tour
        dist_matrix: look up table for get dist city1 and city2
    return:
        new_tour: tour after modify
        improved: boolean
    enumerate all combinations of 3 edges that don't share edges 
    call modify_tour using each combination. 
    break for loops if successfully updated one tour
    if nothing improved, return origin tour and False
    '''
    n = len(tour)
    tour = tour.copy()
    for i in range(n-2):
        for j in range(i+1, n-1):
            for k in range(j+1, n):
                # enumerate by first vertex of edges
                if i == 0 and j == n-2 and k == n-1:
                    continue
                # handling wrap around case (n-2, n-1, 0)
                new_tour, improved = swap_and_reverse(i, j, k, tour, dist_matrix)

                if improved:
                    return new_tour, True

    return tour, False


def swap_and_reverse(i, j, k, tour, dist_matrix, ):
    '''
    args:
        i, j, k: the first vertex of 3 edges
        tour: origin tour
        dist_matrix: distance look up table
    return:
        new_tour: tour after changing
        improved: True if modified from origin tour. False means origin is the best option from 8 cases
    enumerate 7 possible new tours and compare
    '''
    origin_tour = tour.copy()
    n = len(tour)
    segment1 = origin_tour[:i+1]
    segment2 = origin_tour[i+1:j+1]
    segment3 = origin_tour[j+1:k+1]
    segment4 = origin_tour[k+1:]

    improved = False
    best_tour = origin_tour
    min_delta = 0
    a = origin_tour[i]
    b = origin_tour[i+1]
    c = origin_tour[j]
    d = origin_tour[j+1]
    e = origin_tour[k]
    f = origin_tour[(k+1) % n]

    origin_dist = dist_matrix[a][b] + dist_matrix[c][d] + dist_matrix[e][f]

    EPSILON = 1e-9
    # reverse S2
    delta = dist_matrix[a][c] + dist_matrix[b][d] + dist_matrix[e][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment2[::-1] + segment3 + segment4
        best_tour = new_tour
    # reverse S3
    delta = dist_matrix[a][b] + dist_matrix[c][e] + dist_matrix[d][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment2 + segment3[::-1] + segment4
        best_tour = new_tour
    # reverse S2, S3
    delta = dist_matrix[a][c] + dist_matrix[b][e] + dist_matrix[d][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment2[::-1] + segment3[::-1] + segment4
        best_tour = new_tour
    # swap S2, S3
    delta = dist_matrix[a][d] + dist_matrix[e][b] + dist_matrix[c][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment3 + segment2 + segment4
        best_tour = new_tour
    # swap S2, S3, reverse S3
    delta = dist_matrix[a][e] + dist_matrix[d][b] + dist_matrix[c][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment3[::-1] + segment2 + segment4
        best_tour = new_tour
    # swap S2, S3, reverse S2
    delta = dist_matrix[a][d] + dist_matrix[e][c] + dist_matrix[b][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment3 + segment2[::-1] + segment4
        best_tour = new_tour
    # swap S2, S3, reverse S2, S3(equal to reverse 4 and 1)
    delta = dist_matrix[a][e] + dist_matrix[d][c] + dist_matrix[b][f] - origin_dist
    if delta < min_delta-EPSILON:
        min_delta = delta
        new_tour = segment1 + segment3[::-1] + segment2[::-1] + segment4
        best_tour = new_tour
    if min_delta < -1e-9:
        # if min_delta < 0:
        improved = True
    # the only True improved i got here is 12413.412  ->  12413.406 and 12413.406  ->  12413.412
    return best_tour, improved


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    # driver_code('b', solve, False)
    driver_code('b', solve, True)
