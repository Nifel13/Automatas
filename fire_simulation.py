from data_generator import DataGenerator
from simulation_visualizer import FireVisualizer
from hidroplane import Hidroavio
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pygame

class FireSimulation:
    def __init__(self, n, seed, generator_seed = 42):
        self.n = n
        self.generator_seed = generator_seed
        np.random.seed(seed)
        pass
    def generate_data(self):
        data_gen = DataGenerator(self.generator_seed)
        data_gen.generate_data(self.n, "./generated_layers/simulation")
        self.read_data()

    def read_data(self):
        directory = os.fsencode("./generated_layers/")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".doc"): 
                info = self.read_file_info(os.fsdecode(directory) + filename)
                data = self.read_files(os.fsdecode(directory) +filename[:-4], info)
                if filename[:-4] == "simulation_biomes":
                    self.biomes = data
                elif filename[:-4] == "simulation_elevation":
                    self.elevation = data
                elif filename[:-4] == "simulation_humidity":
                    self.humidity = data
                elif filename[:-4] == "simulation_temperature":
                    self.temperature = data
                else:
                    self.vegetation = data
            else:
                continue
        self.fire = np.zeros((self.n, self.n))
        self.fire_time = np.zeros((self.n, self.n))

    def read_files(self, path, metadata):
        rows = int(metadata["rows"])
        data = np.loadtxt(path+".img")
        # reshape field so it has rows rows and columns columns
        data = data.reshape(rows, -1)
        return data
    
    def read_file_info(self, path):
        with open(path, 'r') as file:
            data = file.readlines()
        file_info = {}
        for line in data:
            key, value = line.strip().split(':')
            file_info[key.strip()] = value.strip()
        return file_info
    
    def calculate_wind(self, dx, dy):
        wind = np.empty((self.n, self.n), dtype=tuple)
        for i in range(self.n):
            for j in range(self.n):
                current_altitude = self.elevation[i, j]
                max_neighbour = current_altitude
                ni, nj = i+dx, j+dy
                if 0 <= ni < self.n and 0 <= nj < self.n:
                    max_neighbour = max(current_altitude, self.elevation[ni, nj])
                difference = max_neighbour - current_altitude
                new_dx = dx - (difference * np.sign(dx))
                new_dj = dy - (difference * np.sign(dy))
                wind[i, j] = (new_dx, new_dj)
        return wind


        
    def simulate_fire(self, steps, wind, n_planes = 1):
        self.steps = steps
        self.wind_effect = self.calculate_wind(wind[0], wind[1])
        self.fire_data = self.fire.copy()
        self.biomes_data = self.biomes.copy()
        self.vegetation_data = self.vegetation.copy()
        self.humidity_data = self.humidity.copy()
        self.temperature_data = self.temperature.copy()
        self.elevation_data = self.humidity.copy()
        self.fire_time = np.zeros((self.n, self.n))
        self.planes = np.zeros((self.n, self.n))

        self.max_v = np.max(self.vegetation.flatten())
        self.min_v = np.min(self.vegetation.flatten())
        self.max_h = np.max(self.humidity.flatten())
        self.min_h = np.min(self.humidity.flatten())

        self.states = []
        self.planes_steps = []
        self.hidroavions = []
        for i in range(n_planes): 
            self.hidroavions.append(Hidroavio(np.random.randint(0,self.n-1),np.random.randint(0,self.n-1)))
            self.planes[self.hidroavions[i].x, self.hidroavions[i].y] = 1

        for _ in range(1):
            a = True
            while a:
                x = np.random.randint(0, self.n)
                y = np.random.randint(0, self.n)
                if self.biomes[x,y] != 0:
                    self.fire_data[x, y] = 1
                    a = False

        for iter in range(steps):
            state = self.propagate_fire(wind, iter)
            self.states.append(state[0].copy())
            self.planes_steps.append(state[1].copy())
    def __random_int(self, a, z):
        return np.random.randint(min(a, z), max(a, z) + 1)

    def propagate_fire(self, wind, step):
        """
        4 states:
            0 : no fire
            1 : fire
            2 : big fire (lots of time burning)
            3 : burned
        """
        old_fire_data = self.fire_data.copy()
        for x in range(self.n):
            for y in range(self.n):
                if old_fire_data[x, y] == 1 or old_fire_data[x, y] == 2:
                    self.temperature[x, y] += 1
                    if old_fire_data[x, y] == 1 and self.fire_time[x, y] > 10:
                        self.fire_data[x, y] = 2
                    if self.vegetation_data[x, y] > 0:
                        self.vegetation_data[x, y] -= 1
                    if self.vegetation_data[x, y] == 0:
                        self.fire_data[x, y] = 3
                        continue
                    self.fire_time[x, y] += 1

                    
                    offsets = [(self.__random_int(0, wind[0]), self.__random_int(0, wind[1])) for _ in range(4)]
                    directions = [(-1 + offsets[0][0], 0 + offsets[0][1]),
                        (1 + offsets[1][0], 0 + offsets[1][1]),
                        (0 + offsets[2][0], -1 + offsets[2][1]),
                        (0 + offsets[3][0], 1 + offsets[3][1])]
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.n and 0 <= ny < self.n and old_fire_data[nx, ny] == 0:
                            if (self.humidity_data[nx, ny] < 15*self.fire_data[x, y] + self.temperature[nx, ny]/6) and \
                                self.vegetation_data[nx, ny] > 0 and self.biomes_data[nx, ny] != 0:
                                self.fire_data[nx, ny] = 1
                            elif (self.vegetation_data[nx, ny] > 0 and self.biomes_data[nx, ny] != 0):
                                self.humidity_data[nx, ny] -= self.humidity_data[nx, ny]*0.1
                                if self.humidity_data[nx, ny] < 0:
                                    self.humidity_data[nx, ny] = 0
                                self.temperature[nx, ny] += 5
                            else:
                                self.temperature[nx, ny] += 3 if self.temperature[nx, ny] < 60 else 0
        if step > 20:
            for plane in self.hidroavions:
                self.planes = plane.move_toward(self.humidity_data,self.fire_data,self.planes, self.biomes)
        return self.fire_data, self.planes.copy()
    def visualize_fire_expansion(self):
        pygame.init()
        screen_size = (800, 800)
        screen = pygame.display.set_mode(screen_size)
        clock = pygame.time.Clock()
        
        colors = {
            0: (0, 0, 255),   # Blue for lakes
            1: (0, 255, 0),   # Green for vegetation
            2: (255, 165, 0), # Orange for fire
            3: (255, 255, 255) # White for burned areas
        }

        cell_size = screen_size[0] // self.n
        running = True
        current_step = 0
        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for i in range(self.n):
                for j in range(self.n):
                    x = j * cell_size
                    y = i * cell_size
                    if self.planes_steps[current_step][i, j] == 1:
                        color = (255, 255, 255)
                    elif self.states[current_step][i, j] == 1:
                        color = (255, 165, 0)
                    elif self.states[current_step][i, j] == 2:
                        color = (255, 60, 0)
                    elif self.states[current_step][i, j] == 3:
                        color = (38, 38, 38)
                    elif self.biomes[i, j] == 0:
                        color = (24,59,54)
                    elif self.biomes[i, j] == 1:
                        color = (250, 213, 165)
                    else:
                        vegetation = max((self.vegetation[i][j]/self.max_v)*255 - 40, 0)
                        humidity = 255 - (max((self.humidity[i][j]/self.max_h)*255 - 40, 0))
                        color = ((vegetation + humidity)//2, (vegetation+40 + humidity+20)//2, 30)
                    pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

            pygame.display.flip()
            current_step = (current_step + 1) % self.steps
            clock.tick(10)  # Adjust the frame rate as needed

        pygame.quit()
                    

    
a = FireSimulation(100, seed = 40, generator_seed=2)
a.generate_data()
a.read_data()
a.simulate_fire(1000, (-1,1))
a.visualize_fire_expansion()
print(max(a.states[-1].flatten()))