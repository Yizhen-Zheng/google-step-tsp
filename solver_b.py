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

    tour = iterative_improve(cities, tour, dist_matrix)
    print(calculate_total_distance(tour, dist_matrix))

    return tour


def find_single_combination_to_improve(cities, tour):
    '''
    args:
        cities: the formattted coordinate of each vertex
        tour: the order(indexes of coordinates in cities list) of visit
    '''
    n = len(tour)
    for i in range(n-2):
        for j in range(i+1, n-1):
            for k in range(j+1, n):
                # is's proofed i < j < k
                if i == 0 and j == n-2 and k == n-1:
                    continue
                edge_a_start = cities[tour[i]]
                edge_a_end = cities[tour[i+1]]
                edge_b_start = cities[tour[j]]
                edge_b_end = cities[tour[j+1]]
                edge_c_start = cities[tour[k]]
                edge_c_end = cities[tour[(k+1) % n]]  # the last edge's vertex will be (tour[-1], tour[1])

                best_option_idx = find_best_option(
                    edge_a_start, edge_a_end, edge_b_start, edge_b_end, edge_c_start, edge_c_end)

                if best_option_idx != -1:
                    # if current combination can be improved
                    return (i, j, k, best_option_idx)
    return (-1, -1, -1, -1)


def find_best_option(a1, a2, b1, b2, c1, c2):
    '''
    TODO:This should be optimized by using lookup table(dist) instead of repeatly calculating distance
    args:
        tour: current tour
        cities: city coordinates
        a1, a2, b1, b2, c1, c2: coordinates of edge a,b,c
    pathes between the 3 edges can be splited into:
    segment1=tour[:a1]
    segment2=tour[a2:b2] <-end at b1
    segment3=tour[b2:c2] <-end at c1
    segment4=tour[c2:] <-end at tour[-1]

    (origin)-segment1--a1 - a2--segment2--b1 - b2--segment3--c1 - c2--segment4-(origin)
    '''
    origin_distance = distance(a1, a2)+distance(b1, b2)+distance(c1, c2)

    # keep edge a, reverse segment3
    new_distance1 = distance(b1, c1)+distance(b2, c2)+distance(a1, a2)
    # keep edge b, reverse segment2 and segment3
    new_distance2 = distance(a1, c1)+distance(a2, c2)+distance(b1, b2)
    # keep edge c, reverse segment2
    new_distance3 = distance(a1, b1)+distance(a2, b2)+distance(c1, c2)

    # reverse segment2 and segment3
    new_distance4 = distance(a1, b1)+distance(a2, c1)+distance(b2, c2)
    # reverse segment3, swap segment2 and segment3
    new_distance5 = distance(a1, c1)+distance(a2, b2)+distance(b1, c2)
    # reverse segment2, swap segment2 and segment3
    new_distance6 = distance(a1, b2)+distance(b1, c1)+distance(a2, c2)
    # swap segment2 and segment3
    new_distance7 = distance(a1, b2)+distance(a2, c1)+distance(b1, c2)

    new_distances = [new_distance1, new_distance2, new_distance3,
                     new_distance4, new_distance5, new_distance6, new_distance7]

    # init value: original option
    best_option_idx = -1
    best_delta = 0
    EPSILON = 1e-9
    for option_idx in range(7):
        current_delta = new_distances[option_idx] - origin_distance
        if current_delta < best_delta-EPSILON:
            best_option_idx = option_idx
            best_delta = current_delta

    return best_option_idx


def swap_and_reverse(i, j, k, best_option_idx, tour):
    '''
    follow the best option to modify origin tour
    '''
    segment1 = tour[:i+1]
    segment2 = tour[i+1:j+1]
    segment3 = tour[j+1:k+1]
    segment4 = tour[k+1:]

    match best_option_idx:
        case 0:
            # keep edge a, reverse segment3
            tour = segment1 + segment2 + segment3[::-1] + segment4
        case 1:
            # keep edge b, reverse segment2 and segment3
            tour = segment1 + segment3[::-1] + segment2[::-1] + segment4
        case 2:
            # keep edge c, reverse segment2
            tour = segment1 + segment2[::-1] + segment3 + segment4
        case 3:
            # reverse segment2 and segment3
            tour = segment1 + segment2[::-1] + segment3[::-1] + segment4
        case 4:
            # reverse segment3, swap segment2 and segment3
            tour = segment1 + segment3[::-1] + segment2 + segment4
        case 5:
            # reverse segment2, swap segment2 and segment3
            tour = segment1 + segment3 + segment2[::-1] + segment4
        case 6:
            # swap segment2 and segment3
            tour = segment1 + segment3 + segment2 + segment4

    return tour


def iterative_improve(cities, tour, dist_matrix):
    '''
    keep swapping the first find conbination that can be improved
    break if no more combination to improve found
    '''
    iterate = 0

    while True:
        i, j, k, best_option_idx = find_single_combination_to_improve(cities, tour)
        print(i, j, k, best_option_idx)
        if i == j == k == best_option_idx == -1:
            break
        tour = swap_and_reverse(i, j, k, best_option_idx, tour)
        iterate += 1
        if iterate % 1000 == 0:
            current_total_distance = calculate_total_distance(tour, dist_matrix)
            print('current_total_distance:', current_total_distance)
    return tour


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    # driver_code('b', solve, False)
    driver_code('b', solve, True)
