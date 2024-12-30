import pygame
import sys
from game.color import Color
import json

pygame.init()

class LevelEditor:
    def __init__(self, screen):
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

        # History to undo events
        self.history = []

        # Return to menu button
        self.button_font = pygame.font.SysFont("monospace", 30)
        self.return_button_text = self.button_font.render("Return Menu", True, Color.WHITE)
        self.return_button_rect = self.return_button_text.get_rect(center=(self.screen.width // 2, 30))

    def draw_grid(self):
        for x in range(0, self.screen.width, self.block_size):
            for y in range(0, self.screen.height, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(self.screen.screen, (200, 200, 200), rect, 1)

        self.screen.draw_border()

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
        pygame.display.flip()

    def save_level(self):
        level_data = {
            "player_start": [self.player_start.x, self.player_start.y],
            "key_start": [self.key_start.x, self.key_start.y],
            "door_start": [self.door_start.x, self.door_start.y],
            "blocks": [[block.x, block.y, self.block_size, self.block_size] for block in self.blocks]
        }

        try:
            with open('/home/hytonenj/puzzlegame/data/levels.json', 'r') as f:
                levels = json.load(f)
        except FileNotFoundError:
            levels = []

        levels.append(level_data)

        with open('/home/hytonenj/puzzlegame/data/levels.json', 'w') as f:
            json.dump(levels, f, indent=4)

    def undo_last_action(self):
        if self.history:
            last_action = self.history.pop()
            action_type, rect = last_action
            if action_type == 'block':
                self.blocks.remove(rect)
            elif action_type == 'player':
                self.player_start = None
            elif action_type == 'key':
                self.key_start = None
            elif action_type == 'door':
                self.door_start = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button_rect.collidepoint(event.pos):
                        running = False
                    else:
                        x, y = event.pos
                        x = (x // self.block_size) * self.block_size
                        y = (y // self.block_size) * self.block_size
                        rect = pygame.Rect(x, y, self.block_size, self.block_size)
                        if event.button == 1:  # Left click to place block
                            self.blocks.append(rect)
                            self.history.append(('block', rect))
                        elif event.button == 3:  # Right click to place player
                            self.player_start = rect
                            self.history.append(('player', rect))
                        elif event.button == 2:  # Middle click to place key
                            self.key_start = rect
                            self.history.append(('key', rect))
                        elif event.button == 4:  # Scroll up to place door
                            self.door_start = rect
                            self.history.append(('door', rect))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Press 's' to save the level
                        self.save_level()
                    elif event.key == pygame.K_z:  # Press 'z' to undo the last action
                        self.undo_last_action()

            self.draw_elements()
        self.screen.display_menu()