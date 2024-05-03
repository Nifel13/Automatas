import pygame
import pygame_gui
from time import sleep

def xor(a, b):
    return 1 if (a and not b) or (not a and b) else 0
def nand(a, b):
    return 1 if not (a and b) else 0
def or_func(a, b):
    return 1 if a or b else 0
def and_func(a, b):
    return 1 if a and b else 0
def nor(a, b):
    return 1 if not (a or b) else 0
def xnor(a, b):
    return 1 if (a and b) or (not a and not b) else 0

class CellularAutomaton:
    """
    Class representing a cellular automaton.

    Attributes:
        current_iteration (int): The current iteration of the automaton.
        automaton (list): The state of the automaton.
        rules (dict): Dictionary representing the rules of the automaton.
        steps (int): Number of steps/iterations to generate the automaton.
        screen: Pygame display screen.
        manager: Pygame GUI manager.
        slider: Pygame GUI slider for controlling iterations.
        cell_size (int): Size of each cell in pixels.

    Methods:
        __init__: Initializes the cellular automaton.
        rule: Generates the rule set for the automaton.
        generate_automaton: Generates the cellular automaton based on the given rule number and steps.
        draw_automaton: Draws the cellular automaton using Pygame.
        combine_automatons: Combines two cellular automatons using a specified rule.
    """

    def __init__(self, rule_num: int =None, steps: int=None, state: list =None):
        """
        Initializes the cellular automaton.

        Args:
            rule_num (int, optional): The rule number to generate the automaton.
            steps (int, optional): Number of steps/iterations to generate the automaton.
            state (list, optional): Initial state of the automaton.
        """
        self.current_iteration = 0
        self.automaton = state
        if rule_num is not None and steps is not None:
            self.automaton = self.generate_automaton(rule_num, steps)

    def rule(self, num: int) -> dict:
        """
        Generates the rule set for the automaton.

        Args:
            num (int): The rule number.

        Returns:
            dict: Dictionary representing the rules of the automaton.
        """
        binary = format(num, '08b')
        rules = {format(7 - i, '03b'): binary[i] for i in range(8)}
        return rules

    def generate_automaton(self, rule_num : int , steps: int ) -> list:
        """
        Generates the cellular automaton based on the given rule number and steps.

        Args:
            rule_num (int): The rule number.
            steps (int): Number of steps/iterations.

        Returns:
            list: The generated cellular automaton states.
        """
        self.rules = self.rule(rule_num)
        self.steps = steps
        current_state = ['0'] * self.steps
        current_state[self.steps // 2] = '1'  # Start with one cell in the middle
        automaton = []

        for _ in range(self.steps):
            automaton.append(current_state)
            current_state = ['0'] + current_state + ['0']
            current_state = [self.rules[''.join(current_state[i:i + 3])] for i in range(len(current_state) - 2)]

        return automaton

    def draw_automaton(self, cell_size: float =1):
        """
        Draws the cellular automaton using Pygame.

        Args:
            cell_size (float/int, optional): Size of each cell in pixels.
        """
        pygame.init()
        height = len(self.automaton)
        width = len(self.automaton[0])
        self.screen = pygame.display.set_mode((width * cell_size, height * cell_size + 50))
        pygame.display.set_caption('Cellular Automaton')
        self.manager = pygame_gui.UIManager((width * cell_size, height * cell_size + 50))
        self.slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((0, height * cell_size), (width * cell_size, 50)),
            start_value=0,
            value_range=(0, len(self.automaton) - 1),
            manager=self.manager
        )
        self.cell_size = cell_size
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                        self.current_iteration = int(event.value)
                self.manager.process_events(event)
            self.screen.fill((255, 255, 255))
            for y in range(self.current_iteration + 1):
                for x, cell in enumerate(self.automaton[y]):
                    color = (0, 0, 0) if cell == '1' else (255, 255, 255)
                    pygame.draw.rect(self.screen, color,
                                     pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size,
                                                 self.cell_size))

            self.manager.update(clock.tick(60))
            self.manager.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()

    def combine_automatons(self, automat, rule=xor):
        """
        Combines two cellular automatons using a specified rule.

        Args:
            automat (CellularAutomaton): Another cellular automaton instance.
            rule (function, optional): The combining rule. Default is XOR.

        Returns:
            CellularAutomaton: A new cellular automaton representing the combined state.
        
        Raises:
            ValueError: If the automatons have different numbers of iterations.
        """
        automaton1 = self.automaton
        automaton2 = automat.automaton
        if len(automaton1) != len(automaton2):
            raise ValueError("Automatons must have the same number of iterations")

        combined = []
        for i in range(len(automaton1)):
            combined_row = [str((rule(int(cell1), int(cell2)))) for cell1, cell2 in zip(automaton1[i], automaton2[i])]
            combined.append(combined_row)

        return CellularAutomaton(state=combined)


# Test with rule 139
automaton1 = CellularAutomaton(129, 300)
automaton1.draw_automaton()
automaton2 = CellularAutomaton(30, 300)
automaton3 = CellularAutomaton(5, 300)
combined = automaton1.combine_automatons(automaton2)
combined_2 = combined.combine_automatons(automaton3, rule=or_func)
combined_2.draw_automaton()
