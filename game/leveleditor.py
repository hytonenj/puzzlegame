import pygame
from game.color import Color
import json
import os

pygame.init()

class LevelEditor:
    def __init__(self, screen, level_index=None):
        self.screen = screen
        self.block_size = screen.block_size

        self.BG_COLOR = Color.BLACK
        self.BLOCK_COLOR = Color.GRAY
        self.PLAYER_COLOR = Color.BLUE
        self.KEY_COLOR = Color.YELLOW
        self.DOOR_COLOR = Color.BROWN

        # Level components
        self.blocks = []
        self.player_start = None
        self.key_start = None
        self.door_start = None

        # Levels path
        self.levels_path = os.path.join(os.path.dirname(__file__), '../data/levels.json')

        # Return to menu button
        self.button_font = pygame.font.SysFont("monospace", 30)
        self.return_button_text = self.button_font.render("Return Menu", True, Color.WHITE)
        self.return_button_rect = self.return_button_text.get_rect(center=(self.screen.width // 2, 30))

        # Load levels
        self.load_levels()

        # History for undoing actions
        self.history = []

        # Dropdown menu for selecting level
        self.dropdown_open = False
        self.dropdown_rect = pygame.Rect(self.screen.width - 210, 25, 200, 40)
        self.dropdown_items = [pygame.Rect(self.screen.width - 210, 60 + i * 40, 200, 40) for i in range(len(self.levels))]
        self.selected_level_index = level_index

        # Load existing level if level_index is provided
        if level_index is not None:
            self.load_level(level_index)

    def load_levels(self):
        try:
            with open(self.levels_path, 'r') as f:
                self.levels = json.load(f)
        except FileNotFoundError:
            self.levels = []

    def draw_grid(self):
        for x in range(0, self.screen.width, self.block_size):
            for y in range(0, self.screen.height, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(self.screen.screen, (200, 200, 200), rect, 1)

        self.screen.draw_border()

    def draw_instructions(self):
        instructions = [
            "LMB: Place Block",
            "RMB: Remove Object",
            "1: Place Player",
            "2: Place Key",
            "3: Place Door",
            "S: Save Level"
        ]
        font = pygame.font.SysFont("monospace", 14)
        for i, instruction in enumerate(instructions):
            instruction_text = font.render(instruction, True, Color.WHITE)
            self.screen.screen.blit(instruction_text, (10, 1 + i * 13))

    def draw_dropdown_menu(self):
        font = pygame.font.SysFont("monospace", 18)
        if self.dropdown_open:
            pygame.draw.rect(self.screen.screen, Color.GRAY, self.dropdown_rect)
            dropdown_text = font.render("Select Level", True, Color.WHITE)
            self.screen.screen.blit(dropdown_text, self.dropdown_rect.topleft)
            for i, rect in enumerate(self.dropdown_items):
                pygame.draw.rect(self.screen.screen, Color.GRAY, rect)
                item_text = font.render(f"Level {i + 1}", True, Color.WHITE)
                self.screen.screen.blit(item_text, rect.topleft)
        else:
            pygame.draw.rect(self.screen.screen, Color.GRAY, self.dropdown_rect)
            dropdown_text = font.render("Select Level", True, Color.WHITE)
            self.screen.screen.blit(dropdown_text, self.dropdown_rect.topleft)

    def draw_elements(self):
        self.screen.screen.fill(self.BG_COLOR)
        self.draw_grid()
        for block in self.blocks:
            pygame.draw.rect(self.screen.screen, self.BLOCK_COLOR, block)
        if self.player_start:
            pygame.draw.rect(self.screen.screen, self.PLAYER_COLOR, self.player_start)
        if self.key_start:
            pygame.draw.rect(self.screen.screen, self.KEY_COLOR, self.key_start)
        if self.door_start:
            pygame.draw.rect(self.screen.screen, self.DOOR_COLOR, self.door_start)
        self.screen.screen.blit(self.return_button_text, self.return_button_rect)
        self.draw_dropdown_menu()
        self.draw_instructions()
        pygame.display.flip()

    def save_level(self):
        level_data = {
            "player_start": [self.player_start.x, self.player_start.y],
            "key_start": [self.key_start.x, self.key_start.y],
            "door_start": [self.door_start.x, self.door_start.y],
            "blocks": [[block.x, block.y, self.block_size, self.block_size] for block in self.blocks]
        }

        if self.selected_level_index is not None:
            self.levels[self.selected_level_index] = level_data
        else:
            self.levels.append(level_data)

        with open(self.levels_path, 'w') as f:
            json.dump(self.levels, f, indent=4)

    def load_level(self, level_index):
        try:
            level_data = self.levels[level_index]
            self.player_start = pygame.Rect(*level_data["player_start"], self.block_size, self.block_size)
            self.key_start = pygame.Rect(*level_data["key_start"], self.block_size, self.block_size)
            self.door_start = pygame.Rect(*level_data["door_start"], self.block_size, self.block_size)
            self.blocks = [pygame.Rect(*block) for block in level_data["blocks"]]
        except IndexError:
            print("Level not found")


    def remove_object(self, x, y):
        for block in self.blocks:
            if block.collidepoint(x, y):
                self.blocks.remove(block)
                self.history.append(('block', block))
                return
        if self.player_start and self.player_start.collidepoint(x, y):
            self.history.append(('player', self.player_start))
            self.player_start = None
            return
        if self.key_start and self.key_start.collidepoint(x, y):
            self.history.append(('key', self.key_start))
            self.key_start = None
            return
        if self.door_start and self.door_start.collidepoint(x, y):
            self.history.append(('door', self.door_start))
            self.door_start = None
            return

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button_rect.collidepoint(event.pos):
                        running = False
                    elif self.dropdown_rect.collidepoint(event.pos):
                        self.dropdown_open = not self.dropdown_open
                    elif self.dropdown_open:
                        for i, rect in enumerate(self.dropdown_items):
                            if rect.collidepoint(event.pos):
                                self.selected_level_index = i
                                self.load_level(i)
                                self.dropdown_open = False
                                break
                    else:
                        x, y = event.pos
                        x = (x // self.block_size) * self.block_size
                        y = (y // self.block_size) * self.block_size
                        rect = pygame.Rect(x, y, self.block_size, self.block_size)
                        if event.button == 1:  # Left click to place block
                            self.blocks.append(rect)
                        elif event.button == 3:  # Right click to remove object
                            self.remove_object(x, y)
                elif event.type == pygame.KEYDOWN:
                    x, y = pygame.mouse.get_pos()
                    x = (x // self.block_size) * self.block_size
                    y = (y // self.block_size) * self.block_size
                    rect = pygame.Rect(x, y, self.block_size, self.block_size)
                    if event.key == pygame.K_1:  # Press '1' to place player
                        self.player_start = rect
                    elif event.key == pygame.K_2:  # Press '2' to place key
                        self.key_start = rect
                    elif event.key == pygame.K_3:  # Press '3' to place door
                        self.door_start = rect
                    elif event.key == pygame.K_s:  # Press 's' to save the level
                        self.save_level()
                    elif event.key == pygame.K_z:  # Press 'z' to undo the last action
                        self.undo_last_action()

            self.draw_elements()

        self.screen.display_menu()