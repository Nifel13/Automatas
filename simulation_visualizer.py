import pygame
import numpy as np

class FireVisualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.cell_size = 6
        self.colors = {
            0: (0, 0, 255),  # Water (biome 0)
            1: (0, 255, 0),  # Vegetation
            2: (255, 255, 255),  # Burned
            3: (255, 0, 0),  # Fire
        }

    def visualize(self):
        pygame.init()
        width = self.simulation.n * self.cell_size
        height = self.simulation.n * self.cell_size
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fire Simulation")

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))

            for x in range(self.simulation.n):
                for y in range(self.simulation.n):
                    color = self.colors.get(self.simulation.fire_data[x, y], (0, 0, 0))
                    pygame.draw.rect(screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()