import pandas as pd
import pygame
import numpy as np
import random
import math

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
def generate_bombs(forest,n_bombs):
    n = forest.shape[0]
    bombs = np.zeros((n,n)).astype(str)
    for i in range(n_bombs):
        bombs[random.randint(0,n-1)][random.randint(0,n-1)] = "bomb"
    return bombs

def play_sound_file(sound_file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file_path)
    pygame.mixer.music.play()

import time

def flash_image(screen, image_file):
    # Load the image
    image = pygame.image.load(image_file)

    # Draw the image on the screen
    screen.blit(image, (screen.get_width()//2 - image.get_width()//2, screen.get_height()//2 - image.get_height()//2))

    # Update the display
    pygame.display.flip()

    # Wait for a while
    time.sleep(0.3)
    # Update the display
    pygame.display.flip()

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

                if bombs[x][y] == "bomb":
                    # put on fire all the cells in a radius of r
                    r = 8
                    for i in range(-r, r):
                        for j in range(-r, r):
                            if 0 <= x+i < forest.shape[0] and 0 <= y+j < forest.shape[1]:
                                # Calculate Euclidean distance
                                distance = math.sqrt(i**2 + j**2)
                                if distance <= r:
                                    new_fire[x+i][y+j] = "fire"
                    """play_sound_file("boom.mp3")
                    flash_image(screen,"goodman.png")
                    flash_image(screen,"balqui.jpg")
                    play_sound_file("boom.mp3")
                    flash_image(screen,"adria.jpg")"""
                    new_bombs[x][y] = "burst"
                    
                
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

    return new_forest, new_humidity, new_fire, new_bombs

def scale_color(value, max_value, min_value):
    """scales  a value between 0 and 255"""
    return int(value/ (max_value) * 170) 


forests,max_f,min_f = read_data("combustible","combustible_dades")
humidity,max_h,min_h = read_data("humitat","humitat_dades")
fire = generate_fire(forests,2)
bombs = generate_bombs(forests,15)
print(list(fire))


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
            elif bombs[i][j] == "bomb":
                color = (116, 0, 199)
            else:
                color = (0, scale_color(forest[i][j],max_f,min_f), scale_color(humidity[i][j],max_h,min_h))
            pygame.draw.rect(screen, color, (j * cell_size, i * cell_size, cell_size, cell_size))

# Set up display
n = forests.shape[0]  # size of the matrix
cell_size = 5
width, height = n * cell_size, n * cell_size
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Matrix Visualization")



# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(WHITE)
    forests, humidity, fire,bombs = fire_in_the_forest(forests, humidity, fire, bombs,0,0)
    draw_grid(screen, humidity, forests,fire, bombs, cell_size)
    # print the number of fires
    pygame.display.flip()

# Quit pygame
pygame.quit()
