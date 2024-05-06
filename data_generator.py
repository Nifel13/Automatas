from scipy.ndimage import gaussian_filter
import numpy as np
import random
from perlin_noise import PerlinNoise

class DataGenerator():
    def __init__(self):
        pass

    def generate_elevation(self, wavelength = 1, redistribution = 1):
        noise = PerlinNoise(octaves=10, seed=1)
        xpix, ypix = self.n, self.n
        elevation_data = np.array([[noise([wavelength*(i/xpix), wavelength*(j/ypix)]) for j in range(xpix)] for i in range(ypix)])
        elevation_data += abs(np.min(elevation_data))
        elevation_data *= 100
        print(np.max(elevation_data))
        print(np.power(elevation_data, redistribution))
        return np.power(elevation_data, redistribution)

    def generate_humidity(self, wavelength = 1, redistribution = 0.5):

        noise = PerlinNoise(octaves=2, seed=1)
        xpix, ypix = self.n, self.n
        humidity_data = np.array([[noise([wavelength*(i/xpix), wavelength*(j/ypix)]) for j in range(xpix)] for i in range(ypix)])

        # Scaling
        humidity_data += abs(np.min(humidity_data))
        humidity_data /= np.max(humidity_data)
        humidity_data *= 100
        # return np.random.randint(0, 100, (self.n, self.n))
        return humidity_data
        
    
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
        return temperature, biomes
    
    def generate_vegetation(self, clarianes = 1):
        n = self.n
        vegetation_data = np.round(np.random.normal(50, 20, (n, n)))

        # Afegim clarianes (lo que abans fèiem pels llacs) i afegim deserts
        radius = random.randint(n, n)
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
                        vegetation_data[i, j] = np.abs(np.round(np.random.normal(5, 5)))
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
        self.save_idrisi_layer(self.humidity_data, name+"_humidity", file_title="Humidity")

        temperature, biomes = self.generate_temperature_biome()
        self.save_idrisi_layer(temperature, name+"_temperature", file_title="Temperature")
        self.save_idrisi_layer(biomes, name+"_biomes", file_title="Biomes")

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
                legend cats : 0
                """
        np.savetxt(filename+".img", data.flatten(), fmt="%d")
        with open(filename+".doc", "w") as f:
            f.write(metadata)
