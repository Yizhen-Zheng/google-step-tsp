'''
a file contains helper functions:
read input / write output file
input / output formatter
'''
from typing import Callable
import sys
import math
import csv
from util import calculate_total_distance

INPUT_FILE_NAME = ['./input_0.csv', './input_1.csv', './input_2.csv',
                   './input_3.csv', './input_4.csv', './input_5.csv', './input_6.csv']

CHALLENGES = 7


def distance(city1, city2) -> float:
    '''
    args: coordinates(set) of 2 cities
    return: distance between 2 cities
    used in verify scores, solvers
    '''
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def read_input(filename):
    '''
    args: input file name(see below const)
    return: a list of sets, conatains the coordinate of each city, which will be used by solver function
    '''
    with open(filename) as f:
        cities = []
        for line in f.readlines()[1:]:  # Ignore the first line.
            xy = line.split(',')
            cities.append((float(xy[0]), float(xy[1])))
        return cities


def read_output(solver_idx: str):
    for challenge_number in CHALLENGES:
        file = f'./output_{solver_idx}/output_{challenge_number}.csv'
        with open(file) as f:
            lines = f.readlines()
            assert lines[0].strip() == 'index'
            tour = [int(i.strip()) for i in lines[1:len(lines)]]
    return tour


def format_tour(tour: list[set]) -> str:
    '''
    args: a list of path returned by solver function
    return: a string of formatted tour, 
    can be used for print result, write into .csv 
    '''
    return 'index\n' + '\n'.join(map(str, tour))


def print_tour(tour):
    '''
    args: a list of path returned by solver function
    print a single result
    '''
    print(format_tour(tour))


def write_all_output(solver: Callable, output_dirname: str):
    '''
    write 7 outputs of a single solver into 7 csv file 
    can be used in each solver indipendently
    args:
        solver: the TSP function to find path
        output_dirname: ['a','b', 'c',...]
    will write file like './output_a/output_0.csv'
    '''
    for i in range(CHALLENGES):
        cities = read_input(f'input_{i}.csv')
        tour = solver(cities)
        formatted_tour = format_tour(tour)
        with open(f'output_{output_dirname}/output_{i}.csv', 'w') as f:
            f.write(formatted_tour + '\n')


def write_single_output(solver: Callable, output_dirname: str, data_idx: int = 0):
    '''
    write 1 outputs of a single solver into 1 csv file 
    can be used in each solver indipendently
    args:
        solver: the TSP function to find path
        output_dirname: ['a','b', 'c',...]
        data_idx: [0 - 6]
    will write file like './output_a/output_0.csv'
    '''
    cities = read_input(f'input_{data_idx}.csv')
    tour = solver(cities)
    formatted_tour = format_tour(tour)
    print(formatted_tour)
    with open(f'output_{output_dirname}/output_{data_idx}.csv', 'w') as f:
        f.write(formatted_tour + '\n')


def calculate_path_length(solver_idx: str, file_idx: int):
    '''
    calculate the total path length of a single path
    args:
        solver_idx: ['a', 'b', ...]
        file_idx:[0 - 6]
    '''
    output_file = f'./output_{solver_idx}/output_{file_idx}.csv'
    cities = read_input(f'input_{file_idx}.csv')
    N = len(cities)
    with open(output_file) as f:
        lines = f.readlines()
        assert lines[0].strip() == 'index'
        tour = [int(i.strip()) for i in lines[1:N + 1]]
        assert set(tour) == set(range(N))
        path_length = sum(distance(cities[tour[i]], cities[tour[(i + 1) % N]])
                          for i in range(N))
        print(f'solver_{solver_idx}: input_{file_idx}: {path_length:>10.2f}')


def capy_res_to_visualize(solver_idx: str):
    '''
    args: 
        solver_idx:['a', 'b', ...]
    move ./output_a/output_0.csv into root folder's output_0.csv, etc. by overwrite this ./root/output_0.csv file
    so these can be visualized
    because I cannot figure out the how the js file works 
    '''
    print('copying result to visualizing...')
    for challenge_number in range(CHALLENGES):
        file = f'./output_{solver_idx}/output_{challenge_number}.csv'
        with open(file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            with open(f'output_{challenge_number}.csv', mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                for row in reader:
                    writer.writerow(row)
    print('finished copying')
    return


def driver_code(solver_idx: str, solver: Callable):
    ''' 
    sys.argv[1]: a number between 0 - 6
    if no input idx specified, run code against all inputs
    '''
    print(f'solver_{solver_idx} begins')
    if len(sys.argv) > 1:
        data_idx = int(sys.argv[1])
        print(f'solving with input {data_idx}')
        write_single_output(solver, solver_idx, data_idx)
    else:
        write_all_output(solver, solver_idx)

    capy_res_to_visualize(solver_idx)
    print(f'solver_{solver_idx} finished')

    return
