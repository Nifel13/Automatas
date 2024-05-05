import pygame
import numpy as np

# Define constants
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 4
FPS = 3000
FIRE_COLOR = (255, 0, 0)
HIGH_COLOR = (200, 255, 0)
BURN_COLOR = (0, 0, 0)
VEGETATION_COLOR = (0, 255, 0)
TERRAIN_COLOR = (128, 128, 128)
HUMIDITY_COLOR = (0, 0, 255)

UNBURNED = 0
BURNING = 1
BURNING_HIGH = 2
BURNED = 3

# Function to read IDRISI .img files
def read_idrisi_layer(filename):
    return np.loadtxt(filename+".img")

# Function to visualize data
# Function to visualize data
def visualize_data(screen, terrain_data, vegetation_data, fire_data, lakes_data, paths_data):
    for i in range(terrain_data.shape[0]):
        for j in range(terrain_data.shape[1]):
            rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
              # Blue for lakes  # White for paths
            if vegetation_data[i, j] > 0:
                # Map vegetation values to shades of green
                green_value = min(255, int(vegetation_data[i, j] / 100 * 255))  # Adjust range to fit within 0-255
                pygame.draw.rect(screen, (0, green_value, 0), rect)
            if lakes_data[i, j] == 100:
                pygame.draw.rect(screen, (0, 0, 255), rect)
            if paths_data[i, j] == 1:
                pygame.draw.rect(screen, (255, 255, 255), rect)
            
            if fire_data[i, j] == 1:
                pygame.draw.rect(screen, FIRE_COLOR, rect)
            elif fire_data[i, j] == 2:
                pygame.draw.rect(screen, HIGH_COLOR, rect)
            elif fire_data[i, j] == 3:
                pygame.draw.rect(screen, BURN_COLOR, rect)




def simulate_fire(screen, terrain_data, vegetation_data, humidity_data, wind_velocity_data, lakes_data, paths_data):
    # Initialize fire spread data
    fire_data = np.zeros_like(vegetation_data)
    fire_duration = np.zeros_like(vegetation_data)

    # Start fire at a random location
    start_x, start_y = np.random.randint(0, terrain_data.shape[0]), np.random.randint(0, terrain_data.shape[1])
    fire_data[start_x, start_y] = BURNING
    fire_duration[start_x, start_y] = 1  # Start counting duration

    # Simulation loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        old_fire_data = fire_data.copy()
        # Update fire spread based on rules
        for i in range(1, terrain_data.shape[0] - 1):
            for j in range(1, terrain_data.shape[1] - 1):
                # Check neighboring cells
                neighbors = old_fire_data[i-1:i+2, j-1:j+2]
                if np.any(neighbors == BURNING) or np.any(neighbors == BURNING_HIGH) and fire_data[i, j] == UNBURNED:
                    if np.any(neighbors == BURNING_HIGH):
                        base_fire = 2.5
                    else:
                        base_fire = 1
                    if vegetation_data[i, j] > 0:
                        # Rule 1: The more vegetation, the more probability to burn
                        vegetation_factor = (vegetation_data[i, j] / 50)
                    else:
                        vegetation_factor = 0.9

                    if humidity_data[i, j] < 50:
                        # Rule 2: The more fuel moisture, the more it takes to start catching fire in that cell
                        moisture_factor = 2 - (humidity_data[i, j] / 100)
                    else:
                        moisture_factor = 1

                    if np.abs(terrain_data[i, j] - terrain_data[start_x, start_y]) <= 10:
                        # Rule 3: It's more easy to spread fire to a cell that has similar terrain altitude
                        altitude_factor = 1.3
                    else:
                        altitude_factor = 1.1

                    if wind_velocity_data[i, j] > 5:
                        # Rule 4: It's easier to spread if there's a lot of wind
                        wind_factor = 1.5
                    else:
                        wind_factor = 1

                    if lakes_data[i, j] == 100 or paths_data[i, j] == 1:
                        # Rule 5: You can't catch lakes on fire and paths are more difficult to burn
                        fire_data[i, j] = UNBURNED
                    else:
                        # Apply factors to fire spread probability
                        probability = vegetation_factor * moisture_factor * altitude_factor * wind_factor * base_fire
                        if probability > 2:
                            if fire_data[i, j] == UNBURNED:
                                fire_data[i, j] = BURNING
                                fire_duration[i, j] = 1  # Start counting duration

                if fire_data[i, j] == BURNING:
                    # Rule 7: Cell goes to burned state after a certain duration
                    if fire_duration[i, j] >= (vegetation_data[i, j] / 100)*10:
                        fire_data[i, j] = BURNING_HIGH
                elif fire_data[i, j] == BURNING_HIGH:
                    # Rule 8: Burning high cell goes to burned state after a shorter duration
                    if fire_duration[i, j] >= (vegetation_data[i, j] / 100)*10 + 10:
                        fire_data[i, j] = BURNED

                # Increment fire duration for burning cells
                if fire_data[i, j] in [BURNING, BURNING_HIGH]:
                    fire_duration[i, j] += 1
        # Visualize data
        screen.fill((0, 0, 0))
        visualize_data(screen, terrain_data, vegetation_data, fire_data, lakes_data, paths_data)
        pygame.display.update()
        pygame.time.Clock().tick(FPS)



# Main function
def main():
    global CELL_SIZE
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fire Simulation")

    # Read data files
    terrain_data = read_idrisi_layer("fire_simulation_terrain")
    CELL_SIZE = WIDTH / terrain_data.shape[0]
    vegetation_data = read_idrisi_layer("fire_simulation_vegetation")
    humidity_data = read_idrisi_layer("fire_simulation_humidity")
    wind_velocity_data = read_idrisi_layer("fire_simulation_wind_velocity")
    lakes_data = read_idrisi_layer("fire_simulation_lake")
    paths_data = read_idrisi_layer("fire_simulation_path")

    # Simulate fire propagation
    simulate_fire(screen, terrain_data, vegetation_data, humidity_data,wind_velocity_data, lakes_data, paths_data)

# Entry point
if __name__ == "__main__":
    main()
