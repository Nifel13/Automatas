import pandas as pd
import pygame
import numpy as np
import random
import math
import time

class hidroavio():
    def __init__(self,x,y,charged = False,nearest_fire = False,nearest_water = False):
        self.x = x
        self.y = y
        self.charged = charged
        self.nearest_fire = nearest_fire
        self.nearest_water = nearest_water
        


    def find_nearest_water(self,humidity):
        min_distance = 1000000
        for i in range(humidity.shape[0]):
            for j in range(humidity.shape[1]):
                if humidity[i][j] > 700:
                    distance = math.sqrt((self.x-i)**2 + (self.y-j)**2)
                    if distance < min_distance:
                        min_distance = distance
                        self.nearest_water = (i,j)

    def real_nearest_fire(self,fire):
        min_distance = 1000000
        for i in range(fire.shape[0]):
            for j in range(fire.shape[1]):
                if fire[i][j] == "fire":
                    distance = math.sqrt((self.x-i)**2 + (self.y-j)**2)
                    if distance < min_distance:
                        min_distance = distance
                        self.nearest_fire = (i,j)
    
    def drop_water(self, fire, humidity):
        r = 15
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                nx, ny = self.nearest_fire[0] + i, self.nearest_fire[1] + j
                if 0 <= nx < fire.shape[1] and 0 <= ny < fire.shape[0]:  # Swap the shape indices
                    if humidity[nx][ny] > 40:  # Swap the array indices
                        humidity[nx][ny] = humidity[nx][ny]
                    else:
                        humidity[nx][ny] += 40
                    fire[nx][ny] = "0.0"  # Swap the array indices

        self.find_nearest_water(humidity)

    def move_toward(self,humidity,fire,bombs):
        if self.charged:
            if fire[self.x][self.y] == "fire":
                self.drop_water(fire,humidity)
                self.charged = False
            else:
                self.real_nearest_fire(fire)
                bombs[self.x][self.y] = "0.0"
                if self.x < self.nearest_fire[0]:
                    self.x += 1
                elif self.x > self.nearest_fire[0]:
                    self.x -= 1
                if self.y < self.nearest_fire[1]:
                    self.y += 1
                elif self.y > self.nearest_fire[1]:
                    self.y -= 1
                bombs[self.x][self.y] = "plane"
        else:
            if humidity[self.x][self.y] >= 700:
                self.charged = True
            else:
                if self.nearest_water == False:
                    self.find_nearest_water(humidity)
                bombs[self.x][self.y] = "0.0"
                if self.x < self.nearest_water[0]:
                    self.x += 1
                elif self.x > self.nearest_water[0]:
                    self.x -= 1
                if self.y < self.nearest_water[1]:
                    self.y += 1
                elif self.y > self.nearest_water[1]:
                    self.y -= 1
                bombs[self.x][self.y] = "plane"
    def __str__(self):
        return f"({self.x},{self.y}) charged: {self.charged} nearest_fire: {self.nearest_fire} nearest_water: {self.nearest_water}"

def read_data(field,dades):
    dades = pd.read_csv(dades+".csv")
    rows = dades["rows"][0]
    field = pd.read_csv(field+".csv")
    # reshape field so it has rows rows and columns columns
    field = field.values.reshape(rows, -1)
    field = field[:rows]
    max = dades["max"][0]
    min = dades["min"][0]
    return field, max, min

def generate_fire(forest,fires):
    n = forest.shape[0]
    fire = np.zeros((n,n)).astype(str)
    for i in range(fires):
        fire[random.randint(0,n-1)][random.randint(0,n-1)] = "fire"
    return fire

def random_int(a,z):
    if z >= 0:
        return random.randint(0, z)
    else:
        return random.randint(z, 0)
def generate_objects(forest,n_bombs,n_planes):
    n = forest.shape[0]
    planes = []
    bombs = np.zeros((n,n)).astype(str)
    for i in range(n_bombs):
        bombs[random.randint(0,n-1)][random.randint(0,n-1)] = "bomb"
    for i in range(n_planes): 
        planes.append(hidroavio(random.randint(0,n-1),random.randint(0,n-1)))
        bombs[planes[i].x][planes[i].y] = "plane"
    return bombs,planes


def fire_in_the_forest(forest, humidity,fire,bombs,windx=0,windy=0):
    new_humidity = humidity.copy()
    new_forest = forest.copy()
    new_fire = fire.copy()
    new_bombs = bombs.copy()


    # Iterate over each cell in the forest
    for x in range(forest.shape[0]):
        for y in range(forest.shape[1]):
            # If the cell is on fire
            if fire[x][y] == "fire":
                # Reduce the forest
                if forest[x][y] > 0:
                    new_forest[x][y] -= 1
                else:
                    new_fire[x][y] = "burnt"
                
                for dx, dy in [(-1+random_int(0,windx), 0+random_int(0,windy)), (1+random_int(0,windx), 0+random_int(0,windy)), (0+random_int(0,windx), -1+random_int(0,windy)), (0+random_int(0,windx), 1+random_int(0,windy))]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < forest.shape[0] and 0 <= ny < forest.shape[1] and
                        forest[nx][ny] > 0  and humidity[nx][ny] == 0):
                        new_fire[nx][ny] = "fire"

                    elif (0 <= nx < forest.shape[0] and 0 <= ny < forest.shape[1] and
                        forest[nx][ny] >0  and humidity[nx][ny] > 0):
                        new_humidity[nx][ny] -= 10
                        if new_humidity[nx][ny] < 0:
                            new_humidity[nx][ny] = 0

            if bombs[x][y] == "plane":
                    for plane in planes:
                        plane.move_toward(new_humidity,new_fire,new_bombs)

    return new_forest, new_humidity, new_fire, new_bombs

def scale_color(value, max_value, min_value):
    """scales  a value between 0 and 255"""
    return int(value/ (max_value) * 170) 


# INICIALITZACIÓ
forests,max_f,min_f = read_data("combustible","combustible_dades")
humidity,max_h,min_h = read_data("humitat","humitat_dades")
print(max_f,min_f,max_h,min_h)
fire = generate_fire(forests,2)
bombs,planes = generate_objects(forests,0,1)


# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Function to draw the grid
def draw_grid(screen, humidity,forest,fire,bombs, cell_size):
    n = len(humidity)
    for i in range(n):
        for j in range(n):
            if fire[i][j] == "fire":
                color = (2*forest[i][j]+random.randint(0,30), 0, 0)
            elif fire[i][j] == "burnt":
                color = (0, 0, 0)
            elif bombs[i][j] == "plane":
                color = (243, 255, 130)
            else:
                color = (0, scale_color(forest[i][j],max_f,min_f), scale_color(humidity[i][j],max_h,min_h))
            pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))



# Set up display
n = forests.shape[0]  # size of the matrix
cell_size = 4
width, height = n * cell_size, n * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Matrix Visualization")

font = pygame.font.Font(None, 36)

# Initialize iteration counter
iteration = 0

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(WHITE)
    forests, humidity, fire,bombs = fire_in_the_forest(forests, humidity, fire, bombs,0,0)
    draw_grid(screen, humidity, forests,fire, bombs, cell_size)
    text = font.render(f"Iteration: {iteration}", True, (255, 255, 255))
    text_background = pygame.Surface(text.get_size())
    text_background.fill(WHITE)
    screen.blit(text, (10, 10))
    # print the number of fires
    iteration += 1
    pygame.display.flip()

# Quit pygame
pygame.quit()
