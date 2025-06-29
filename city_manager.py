import numpy as np
import pandas as pd
import os
import gc
import pickle
import csv


class CityManager:
    def __init__(self, solver_idx, input_idx):
        self.work_dir = f'output_{solver_idx}/cached/{input_idx}/'  # depends on solver_idx and which input file[5,6,7]
        self.global_distance_matrix_file_path = f'{self.work_dir}global_distance_matrix.pkl'
        self.subcity_files_path = []
        self.local_solutions_files_path = []
        os.makedirs(self.work_dir, exist_ok=True)

    def create_and_save_global_distance_matrix(self, cities, dist_matrix_creater: callable):
        '''
        args: 
            the global dist matrix creater function
        store the created dist_matrix to cache
        '''
        dist_matrix = dist_matrix_creater(cities)
        with open(self.global_distance_matrix_file_path, 'wb')as f:
            pickle.dump(dist_matrix, f)
        print(f'global matrix saved to: {self.global_distance_matrix_file_path} ')
        # remove the global matrix(N*N) from memory
        gc.collect()

    def split_and_save_subcities(self, cities, city_spliter: callable):
        '''
        split self.cities into subcities, 
        save each subcity group into CSV with origin indexes
        save file names of subcities to self.subcit_file_path 
        args: city_spliter, a function that returns a list of subcities
        '''
        N = len(cities)
        # dicide how many subcities to split
        row_length = 0
        if 512 <= N < 2048:
            row_length = 2
        elif 2048 <= N < 5000:
            row_length = 3
        elif N > 5000:
            row_length = 9

        subcities = city_spliter(cities, row_length)
        for i in range(len(subcities)):  # for each subcity in origin cities, create it's own cities file
            subcity = subcities[i]
            filename = f'{self.work_dir}sub_cities_{i}.csv'
            with open(filename, 'w', newline='')as f:
                writer = csv.writer(f)
                writer.writerow(['origin_idx', 'x', 'y'])
                for city_idx, x, y in subcity:
                    writer.writerow([city_idx, x, y])
            self.subcity_files_path.append((i, filename))
            print(f"Saved subcity {i} with {len(subcity)} cities to {filename}")

    def read_single_subcity(self, subcity_idx):
        '''
        read a single subcity csv to subcity list 
        args:
            subcity_file_path: single subcity csv file path,will be like subcities_i.csv, where i is in subcity numbers(4,9,16...)
                the subcity_file file should have row (origin_idx, x, y)
        return: 
            cities read from subcity_file_path, will be passed to solver
        '''
        data_frame = pd.read_csv(self.subcity_files_path[subcity_idx])
        local_cities = [(row['x'], row['y'])for _, row in data_frame.iterrows()]
        return local_cities

    def write_single_subcity_solution(self, subcity_idx, local_solution):
        '''
        args:
            subcity_solution_file_path: the file to write solution
                subcity_solution_file_path can be get from self.local_solutions_files_path
        '''
        # Save solution
        local_solution_file_path = f'{self.work_dir}local_solution_{subcity_idx}.csv'
        self.local_solutions_files_path.append(local_solution_file_path)

        with open(local_solution_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['local_idx'])
            for local_city_idx in local_solution:
                writer.writerow([local_city_idx])

    def convert_to_global_tour(self):
        '''
        read saved tour_array, convert local idx into origin idx
        return: a list contains converted sub tours
        '''
        N = len(self.subcity_files_path)
        tour_array = []
        for i in range(N):
            # read (origin_idx, x, y) of subcities
            subcity_data_frame = pd.read_csv(self.subcity_files_path[i])
            origin_indexes = subcity_data_frame['origin_idx'].tolist()
            # read local solution
            local_solution_data_frame = pd.read_csv(self.local_solutions_files_path[i])
            local_solution = local_solution_data_frame['local_idx'].tolist()
            # convert to global idx
            global_solution = []
            for local_idx in local_solution:
                global_solution.append(origin_indexes[local_idx])
            tour_array.append(global_solution)
        return tour_array

    def read_dist_matrix(self):
        '''
        read saved global dist_matrix
        '''
        dist_matrix_file = self.global_distance_matrix_file_path
        with open(dist_matrix_file, 'rb') as f:
            global_dist_matrix = pickle.load(f)
        return global_dist_matrix
