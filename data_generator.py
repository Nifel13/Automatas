from scipy.ndimage import gaussian_filter
import numpy as np
import random
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt

class DataGenerator():
    def __init__(self, seed = 42, n = 100):
        self.seed = seed
        self.n = n
        pass

    def generate_elevation(self, wavelength = 0.5, redistribution = 1.05):
        noise = PerlinNoise(octaves=6, seed=self.seed)
        xpix, ypix = self.n, self.n
        elevation_data = np.array([[noise([wavelength*((i/xpix)-0.5), wavelength*((j/ypix)-0.5)]) for j in range(xpix)] for i in range(ypix)])
        elevation_data += abs(np.min(elevation_data))
        elevation_data *= 100
        return np.power(elevation_data, redistribution)
    
    def visualize_elevation(self):
        elevation_data = self.generate_elevation()
        plt.figure(figsize=(8, 6))
        plt.imshow(elevation_data, cmap='terrain', origin='lower')
        plt.colorbar(label='Elevation')
        plt.title('Elevation Map')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

    def generate_humidity(self, wavelength = 1, redistribution = 1):

        noise = PerlinNoise(octaves=2, seed=self.seed)
        xpix, ypix = self.n, self.n
        humidity_data = np.array([[noise([wavelength*(i/xpix), wavelength*(j/ypix)]) for j in range(xpix)] for i in range(ypix)])

        # Scaling
        humidity_data += abs(np.min(humidity_data))
        humidity_data /= np.max(humidity_data)
        humidity_data *= 100
        # return np.random.randint(0, 100, (self.n, self.n))
        return np.power(humidity_data, redistribution)
        
    
    def generate_temperature_biome(self, nivell_mar = 40, nivell_muntanya = 90, jungla = 70, desert = 20):
        """
        La inicialització és dependent de l'altura i l'humitat, però més tard aquesta serà una capa indepedent
        Biome serà una capa que no es modificarà en la simulació. Conté també els llacs. Llistat de biomes:
            0 : mar
            1 : desert
            2 : bosc normal
            3 : jungla
            4 : alta muntanya
        """
        n = self.n
        self.nivell_mar = nivell_mar
        temperature = np.zeros((n,n))
        biomes = np.zeros((n,n))
        for x in range(n):
            for y in range(n):
                if self.elevation_data[x, y] < nivell_mar:
                    # Posem una certa temperatura al mar / llacs
                    temperature[x, y] = 15
                    biomes[x,y] = 0
                elif self.elevation_data[x, y] > nivell_muntanya:
                    temperature[x, y] = 5
                    biomes[x,y] = 4
                else:
                    if self.humidity_data[x, y] < desert:
                        temperature[x, y] = 35
                        biomes[x,y] = 1
                    elif self.humidity_data[x, y] < jungla:
                        temperature[x, y] = 20
                        biomes[x,y] = 2
                    else:
                        temperature[x, y] = 25
                        biomes[x,y] = 3
        self.biomes_data = biomes
        self.add_humidity_near_lakes()
        return temperature, biomes
    
    def add_humidity_near_lakes(self):
        # Create a copy of the humidity array to avoid modifying the original array
        new_humidity_array = np.copy(self.humidity_data)
        # Iterate over each element in the humidity array
        for i in range(len(new_humidity_array)):
            for j in range(len(new_humidity_array[0])):
                if self.biomes_data[i][j] == 0:
                    for dx in range(-5, 6):
                        for dy in range(-5, 6):
                            x, y = i + dx, j + dy
                            if 0 <= x < len(new_humidity_array) and 0 <= y < len(new_humidity_array[0]):
                                new_humidity_array[x][y] += 10 if new_humidity_array[x][y] < 100 else 0
        self.humidity_data = new_humidity_array
    
    def generate_vegetation(self, clarianes = 1):
        n = self.n
        vegetation_data = np.round(np.random.normal(50, 20, (n, n)))

        # Afegim clarianes (lo que abans fèiem pels llacs) i afegim deserts
        radius = 50
        center_x, center_y = random.randint(0, n), random.randint(0, n)
        deformation_factor = 0
        for _ in range(clarianes):
            for i in range(n):
                for j in range(n):
                    if (i - center_x)**2 + (j - center_y)**2 < radius**2 + deformation_factor:
                        vegetation_data[i, j] = np.round(np.random.normal(20, 10))
                    deformation_factor += random.randint(-20, 20)

        for i in range(n):
            for j in range(n):
                if self.biomes_data[i, j] == 1:
                    vegetation_data[i, j] = np.abs(np.round(np.random.normal(2, 2)))
                elif self.biomes_data[i, j] == 3:
                    vegetation_data[i, j] = np.round(np.random.normal(70, 10))
                elif self.biomes_data[i, j] == 4:
                    # les muntanyes són com clarianes
                    vegetation_data[i, j] = np.round(np.random.normal(20, 10))

        vegetation_data = gaussian_filter(vegetation_data, sigma=1)
        return vegetation_data


    def generate_data(self, n, name):
        self.n = n
        self.elevation_data = self.generate_elevation()
        self.save_idrisi_layer(self.elevation_data, name+"_elevation", file_title="Elevation")

        self.humidity_data = self.generate_humidity()

        temperature, biomes = self.generate_temperature_biome()
        self.save_idrisi_layer(temperature, name+"_temperature", file_title="Temperature")
        self.save_idrisi_layer(biomes, name+"_biomes", file_title="Biomes")

        self.save_idrisi_layer(self.humidity_data, name+"_humidity", file_title="Humidity")


        vegetation = self.generate_vegetation()
        self.save_idrisi_layer(vegetation, name+"_vegetation", file_title="Vegetation")


    def save_idrisi_layer(self, data, filename, file_title="Untitled", columns=1, rows=None, min_x=0, max_x=None,
                      min_y=0, max_y=None, resolution=1, min_value=None, max_value=None, value_units="unspecified"):
        if rows is None:
            rows = data.shape[0]
        if max_x is None:
            max_x = min_x + data.shape[1] * resolution
        if max_y is None:
            max_y = min_y + data.shape[0] * resolution
        if max_value is None:
            max_value = np.max(data)
        if min_value is None:
            min_value = np.min(data)
        
        metadata = f"""file title  : {file_title}
data type   : string
file type   : ascii
columns     : {columns}
rows        : {rows}
ref.system  : plane
ref.units   : m
unit dist.  : {resolution}
min. X      : {min_x}
max. X      : {max_x}
min. Y      : {min_y}
max. Y      : {max_y}
pos 'n error: unknown
resolution  : {resolution}
min. value  : {min_value}
max. value  : {max_value}
Value units : {value_units}
Value Error : unknown
flag Value  : none
flag def 'n : none
legend cats : 0"""
        np.savetxt(filename+".img", data.flatten(), fmt="%d")
        with open(filename+".doc", "w") as f:
            f.write(metadata)

seed = 123  # Example seed value
n = 100  # Example size of the elevation map
my_object = DataGenerator(seed, n)
my_object.generate_elevation()
my_object.visualize_elevation()