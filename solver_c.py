from common import driver_code
from util import calculate_total_distance, construct_dist_matrix_zero, distance
import sys
import random
import math

INIT_TEMP = 1000000000
COOLING_RATE = 0.99999


def solve(cities):
    '''
    args: cities: the formattted coordinate of each vertex
    return: tour: the order(indexes of coordinates in cities list) of visit
    first randomly place all cities
    then resolve all crosses using simulated annealing
    calculate_total_distance seems can be currified (return a function that can access closure dist_matrix, so won't need to pass dist_matrix everywhere)
    '''

    # a N*N matrix represent distance between every 2 cities, where N is total city number for quick lookup
    dist_matrix = construct_dist_matrix_zero(cities)
    tour = list(range(len(cities)))
    # randomly place tour as initial value
    random.shuffle(tour)
    current_dist = calculate_total_distance(tour, dist_matrix)
    print('init distance:', current_dist)
    tour, distance = simulated_annealing(tour, cities, dist_matrix)
    print(distance)
    return tour


def simulated_annealing(tour, cities, dist_matrix):
    '''
    args:
        randomly initialized tour(a list of cities' index)
        cities coordinates
    return:
        optimizd tour
    '''
    # initialize temp, best tour, best total distance
    current_temp = INIT_TEMP
    best_total_distance = calculate_total_distance(tour, dist_matrix)
    # shallow copy if ok since tour only contains primitive data(int), avoid modifying tour when new accepted tour is not best
    best_tour = tour.copy()
    # initialize current total distance
    current_total_distance = best_total_distance
    current_tour = tour

    iteration = 0
    while current_temp > 1:
        if iteration % 100 == 0:
            print(current_temp)
            print('current:', current_total_distance)
            print('best:', best_total_distance)
        # find a new option
        new_tour = find_new_tour(current_tour)
        new_tour_total_distance = calculate_total_distance(new_tour, dist_matrix)

        # accept or reject mechanism
        if random.random() < calculate_acceptance_probability(current_total_distance, new_tour_total_distance, current_temp):
            # update current if accept
            current_tour = new_tour
            current_total_distance = new_tour_total_distance

            if current_total_distance < best_total_distance:
                # update best if current is better than best
                best_total_distance = current_total_distance
                best_tour = current_tour

        # cool down current temp
        current_temp = current_temp*COOLING_RATE
        iteration += 1
    return (best_tour, best_total_distance)


def find_new_tour(current_tour):
    '''
    args:
        cities: the formattted coordinate of each vertex
        current_tour: current indexes of cities
    return:
        new_tour:
    generate a new_tour option by swapping 2 cities randomly (similar to 2-opt, but may get worse)
    '''
    new_tour = current_tour.copy()
    i, j = sorted(random.sample(current_tour, 2))
    # pick 2 cities to randomly swap. make sure i < j to slice list
    new_tour[i:j+1] = new_tour[i:j+1][::-1]
    # swap 2 cities and reverse all inbetween to form a path

    return new_tour


def calculate_acceptance_probability(current_total_distance, new_tour_total_distance, current_temp):
    '''
    if new tour is better, accept 
    if new tour is worse: Metropolis criterion
        calculate the difference between current and new tour's total distance, the worse new option is, the less probability to accept
        divide delta distance by temprature. higher temprature will increase probability of accepting worse new option
    '''
    if current_total_distance > new_tour_total_distance:
        # if new option is better, accept
        return 1.0
    probability = math.exp((current_total_distance-new_tour_total_distance)/current_temp)
    return probability


if __name__ == '__main__':
    ''' sys.argv[1]: a number between 0 - 6'''
    driver_code('c', solve)
