def rule(num):
    binary = format(num, '08b')
    rules = {format(7 - i, '03b'): binary[i] for i in range(8)}
    return rules

def cellular_automaton(rule_num, steps):
    rules = rule(rule_num)
    current_state = ['0'] * steps
    current_state[steps // 2] = '1'  # Start with one cell in the middle

    for _ in range(steps):
        line = ''.join(current_state).replace('0', '  ').replace('1', '██')
        print(line.center(steps))  # Center the output
        current_state = ['0'] + current_state + ['0']
        current_state = [rules[''.join(current_state[i:i+3])] for i in range(len(current_state) - 2)]

# Test with rule 45
import pygame
from time import sleep

def rule(num):
    binary = format(num, '08b')
    rules = {format(7 - i, '03b'): binary[i] for i in range(8)}
    return rules

def cellular_automaton(rule_num, steps):
    rules = rule(rule_num)
    current_state = ['0'] * steps
    current_state[steps // 2] = '1'  # Start with one cell in the middle
    automaton = []

    for _ in range(steps):
        automaton.append(current_state)
        current_state = ['0'] + current_state + ['0']
        current_state = [rules[''.join(current_state[i:i+3])] for i in range(len(current_state) - 2)]
    
    return automaton

import pygame_gui

def draw_automaton(automaton, cell_size=1):
    pygame.init()
    height = len(automaton)
    width = len(automaton[0])
    screen = pygame.display.set_mode((width * cell_size, height * cell_size + 50))  # Extra space for slider
    pygame.display.set_caption('Cellular Automaton')

    manager = pygame_gui.UIManager((width * cell_size, height * cell_size + 50))
    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((0, height * cell_size), (width * cell_size, 50)),
        start_value=0,
        value_range=(0, len(automaton) - 1),
        manager=manager
    )

    clock = pygame.time.Clock()  # Create a clock object
    running = True
    current_iteration = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    current_iteration = int(event.value)

            manager.process_events(event)

        screen.fill((255, 255, 255))  # Clear screen

        for y in range(current_iteration + 1):  # Draw all past iterations up to current one
            for x, cell in enumerate(automaton[y]):
                color = (0, 0, 0) if cell == '1' else (255, 255, 255)
                pygame.draw.rect(screen, color, pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size))

        manager.update(clock.tick(60))  # Update manager
        manager.draw_ui(screen)  # Draw UI

        pygame.display.flip()

    pygame.quit()
def xor(a,b):
    return 1 if (a and not b) or (not a and b) else 0

def nand(a,b):
    return 1 if not (a and b) else 0

def or_func(a,b):
    return 1 if a or b else 0

def and_func(a,b):
    return 1 if a and b else 0

def combine_automatons(automaton1, automaton2, rule=xor):
    if len(automaton1) != len(automaton2):
        raise ValueError("Automatons must have the same number of iterations")

    combined = []
    for i in range(len(automaton1)):
        combined_row = [str((rule(int(cell1), int(cell2)))) for cell1, cell2 in zip(automaton1[i], automaton2[i])]
        combined.append(combined_row)

    return combined

# Test with rule 139
automaton1 = cellular_automaton(225, 700)
automaton2 = cellular_automaton(30, 700)
automaton3 = cellular_automaton(5, 700)
combined = combine_automatons(automaton1, automaton2)
combined_2 = combine_automatons(combined, automaton3, rule=nand)
draw_automaton(combined_2, cell_size=1)