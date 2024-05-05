import pandas as pd
import numpy as np
import random
from scipy.ndimage import gaussian_filter

def save_idrisi_layer(data, filename, file_title="Untitled", columns=1, rows=None, min_x=0, max_x=None,
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
    np.savetxt(filename+".img", data, fmt="%d")
    with open(filename+".doc", "w") as f:
        f.write(metadata)


def generate_fire_propagation_data(n, name, terrain_type="flat", vegetation_type="dense", lakes=1, paths=1):
    # Generate terrain
    terrain_data = generate_terrain(n, terrain_type)
    save_idrisi_layer(terrain_data, name+"_terrain")

    # Generate humidity
    humidity_data = generate_humidity(n)
    save_idrisi_layer(humidity_data, name+"_humidity")

    # Generate vegetation (fuel)
    vegetation_data = generate_vegetation(n, vegetation_type)
    save_idrisi_layer(vegetation_data, name+"_vegetation")

    # Generate topography
    topography_data = generate_topography(n)
    save_idrisi_layer(topography_data, name+"_topography")

    # Generate wind velocity
    wind_velocity_data = generate_wind_velocity(n)
    save_idrisi_layer(wind_velocity_data, name+"_wind_velocity")

    # Generate fuel moisture
    fuel_moisture_data = generate_fuel_moisture(n)
    save_idrisi_layer(fuel_moisture_data, name+"_fuel_moisture")

    # Generate lakes
    lakes_data = np.zeros((n, n))
    for i in range(lakes):
        lake_data = generate_lake(n)
        lakes_data += lake_data
    save_idrisi_layer(lakes_data, name+f"_lake")

    # Generate paths
    paths_data = np.zeros((n, n))
    for i in range(paths):
        path_data = generate_path(n)
        paths_data += path_data
    save_idrisi_layer(paths_data, name+f"_path")

def generate_terrain(n, terrain_type):
    if terrain_type == "flat":
        return np.zeros((n, n))
    elif terrain_type == "hilly":
        return np.random.normal(50, 10, (n, n))
    elif terrain_type == "mountainous":
        return np.random.normal(100, 20, (n, n))
    else:
        raise ValueError("Invalid terrain type")

def generate_humidity(n):
    return np.random.randint(0, 100, (n, n))

def generate_vegetation(n, vegetation_type, zone_divisions=4, dense_probability=0.3):
    vegetation_data = gaussian_filter(np.random.randint(40, 100, (n, n)), sigma=1)

    # Afegim clarianes
    for _ in range(random.randint(1, 8)):
        radius = random.randint(n//zone_divisions**2, n//zone_divisions**2)
        center_x, center_y = random.randint(0, n), random.randint(0, n)
        deformation_factor = 0
        for i in range(n):
            for j in range(n):
                if (i - center_x)**2 + (j - center_y)**2 < radius**2 + deformation_factor:
                    vegetation_data[i, j] = np.random.randint(10, 60)
                deformation_factor += random.randint(-20, 20)

    # Apply Gaussian filter for smoothing
    vegetation_data = gaussian_filter(vegetation_data, sigma=1)

    return vegetation_data

def generate_zone_vegetation(zone_size, vegetation_type):
    if vegetation_type == "dense":
        return gaussian_filter(np.random.randint(40, 100, (zone_size, zone_size)), sigma=1)
    elif vegetation_type == "sparse":
        return gaussian_filter(np.random.randint(20, 60, (zone_size, zone_size)), sigma=1)
    else:
        raise ValueError("Invalid vegetation type")


def generate_topography(n):
    return np.random.normal(0, 1, (n, n))

def generate_wind_velocity(n):
    return np.random.randint(0, 10, (n, n))

def generate_fuel_moisture(n):
    return np.random.randint(0, 100, (n, n))

def generate_lake(n):
    lake_data = np.zeros((n, n))
    radius = random.randint(n//8, n//4)
    center_x, center_y = random.randint(0, n), random.randint(0, n)
    deformation_factor = 0
    for i in range(n):
        for j in range(n):
            if (i - center_x)**2 + (j - center_y)**2 < radius**2 + deformation_factor:
                lake_data[i, j] = 100
            deformation_factor += random.randint(-15, 15)
    return lake_data

def generate_path(n, path_width=0):
    path_data = np.zeros((n, n))
    start_x, start_y = random.randint(0, n-1), random.randint(0, n-1)
    end_x, end_y = random.randint(0, n-1), random.randint(0, n-1)
    current_x, current_y = start_x, start_y
    path_data[current_x, current_y] = 1

    length = 0
    
    while (current_x, current_y) != (end_x, end_y) and length < 200:
        direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = current_x + direction[0]
        new_y = current_y + direction[1]
        if 0 <= new_x < n and 0 <= new_y < n:
            path_data[new_x, new_y] = 1
            current_x, current_y = new_x, new_y
            
            # Add adjacent cells to make the path wider
            for i in range(-path_width//2 + 1, path_width//2 + 1):
                for j in range(-path_width//2 + 1, path_width//2 + 1):
                    if 0 <= new_x + i < n and 0 <= new_y + j < n:
                        path_data[new_x + i, new_y + j] = 1
        length += 1
    
    return path_data



# Example usage
generate_fire_propagation_data(100, "fire_simulation", terrain_type="flat", vegetation_type="dense", lakes=2, paths=1)
