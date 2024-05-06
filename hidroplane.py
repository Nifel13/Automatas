import math
import numpy

class Hidroavio():
    def __init__(self,x,y,charged = False,nearest_fire = False,nearest_water = False):
        self.x = x
        self.y = y
        self.charged = charged
        self.nearest_fire = nearest_fire
        self.nearest_water = nearest_water
        


    def find_nearest_water(self,biome):
        min_distance = float("inf")
        for i in range(biome.shape[0]):
            for j in range(biome.shape[1]):
                if biome[i, j] == 0:
                    distance = math.sqrt((self.x-i)**2 + (self.y-j)**2)
                    if distance < min_distance:
                        min_distance = distance
                        self.nearest_water = (i,j)

    def real_nearest_fire(self,fire):
        min_distance = float("inf")
        for i in range(fire.shape[0]):
            for j in range(fire.shape[1]):
                if fire[i, j] in [1, 2]:
                    distance = math.sqrt((self.x-i)**2 + (self.y-j)**2)
                    if distance < min_distance:
                        min_distance = distance
                        self.nearest_fire = (i,j)
    
    def drop_water(self, fire, humidity):
        r = 5
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                if i+j <= int(r*1.2):
                    nx, ny = self.nearest_fire[0] + i, self.nearest_fire[1] + j
                    if 0 <= nx < fire.shape[1] and 0 <= ny < fire.shape[0]:  # Swap the shape indices
                        if humidity[nx][ny] > 70:  # Swap the array indices
                            humidity[nx][ny] = humidity[nx][ny]
                        else:
                            humidity[nx][ny] += 40
                        fire[nx,ny] = 0  # Swap the array indices

        self.find_nearest_water(humidity)

    def move_toward(self,humidity,fire,bombs, biomes):
        if self.charged:
            if fire[self.x, self.y] in [1, 2]:
                self.real_nearest_fire(fire)
                self.drop_water(fire,humidity)
                self.charged = False
            else:
                self.real_nearest_fire(fire)
                bombs[self.x,self.y] = 0
                if self.x < self.nearest_fire[0]:
                    self.x += 1
                elif self.x > self.nearest_fire[0]:
                    self.x -= 1
                if self.y < self.nearest_fire[1]:
                    self.y += 1
                elif self.y > self.nearest_fire[1]:
                    self.y -= 1
                bombs[self.x, self.y] = 1
        else:
            if biomes[self.x, self.y] == 0:
                self.charged = True
            else:
                if self.nearest_water == False:
                    self.find_nearest_water(biomes)
                bombs[self.x, self.y] = 0
                if self.x < self.nearest_water[0]:
                    self.x += 1
                elif self.x > self.nearest_water[0]:
                    self.x -= 1
                if self.y < self.nearest_water[1]:
                    self.y += 1
                elif self.y > self.nearest_water[1]:
                    self.y -= 1
                bombs[self.x, self.y] = 1
        return bombs
    def __str__(self):
        return f"({self.x},{self.y}) charged: {self.charged} nearest_fire: {self.nearest_fire} nearest_water: {self.nearest_water}"