import pygame
import json
import os
import logging
from game.block import Block
from game.player import Player
from game.key import Key
from game.door import Door
from game.color import Color
from game.teleport import Teleport, TeleportPair

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

pygame.init()

class LevelEditor:
    def __init__(self, screen, level_index=None):
        logging.info("Initializing LevelEditor")
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
        self.teleports = []

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
        self.dropdown_rect = pygame.Rect(self.screen.width - 220, 0, 200, 80)
        self.dropdown_items = [pygame.Rect(self.screen.width - 220, 80 + i * 40, 200, 40) for i in range(len(self.levels))]
        self.selected_level_index = level_index

        # Load existing level if level_index is provided
        if level_index is not None:
            self.load_level(level_index)

    def load_level(self, level_index):
        try:
            logging.info(f"Loading level {level_index + 1}")
            level_data = self.levels[level_index]
            self.player_start = Player(level_data["player_start"][0], level_data["player_start"][1], self.block_size, self.block_size)
            self.key_start = Key(level_data["key_start"][0], level_data["key_start"][1], self.block_size, self.block_size)
            self.door_start = Door(level_data["door_start"][0], level_data["door_start"][1], self.block_size, self.block_size)
            self.blocks = [Block(*block) for block in level_data["blocks"]]
            self.teleports = [TeleportPair(teleport[0][0], teleport[0][1], teleport[1][0], teleport[1][1], self.block_size, self.block_size) for teleport in level_data.get("teleports", [])]
        except IndexError:
            logging.error("Level not found")

    def load_levels(self):
        try:
            logging.info("Loading levels from file")
            with open(self.levels_path, 'r') as f:
                self.levels = json.load(f)
        except FileNotFoundError:
            logging.warning("Levels file not found, initializing with empty levels")
            self.levels = []

    def save_level(self):
        logging.info("Saving current level")
        # Validation checks
        if not self.player_start:
            logging.error("Cannot save level: Player is missing")
            return
        if not self.key_start:
            logging.error("Cannot save level: Key is missing")
            return
        if not self.door_start:
            logging.error("Cannot save level: Door is missing")
            return
        if not self.blocks:
            logging.error("Cannot save level: At least one block is required")
            return
        
        level_data = {
            "player_start": [self.player_start.rect.x, self.player_start.rect.y],
            "key_start": [self.key_start.rect.x, self.key_start.rect.y],
            "door_start": [self.door_start.rect.x, self.door_start.rect.y],
            "blocks": [[block.rect.x, block.rect.y, block.rect.width, block.rect.height, block.can_move] for block in self.blocks],
            "teleports": [[[teleport.teleport1.rect.x, teleport.teleport1.rect.y, teleport.teleport1.rect.width, teleport.teleport1.rect.height],
                        [teleport.teleport2.rect.x, teleport.teleport2.rect.y, teleport.teleport2.rect.width, teleport.teleport2.rect.height]] for teleport in self.teleports]
        }

        if self.selected_level_index is not None:
            self.levels[self.selected_level_index] = level_data
        else:
            self.levels.append(level_data)

        with open(self.levels_path, 'w') as f:
            json.dump(self.levels, f, indent=4)
        logging.info("Level saved successfully")

    def draw_grid(self):
        for x in range(0, self.screen.width, self.block_size):
            for y in range(0, self.screen.height, self.block_size):
                rect = pygame.Rect(x, y, self.block_size, self.block_size)
                pygame.draw.rect(self.screen.screen, (200, 200, 200), rect, 1)

        self.screen.draw_border()

    def draw_instructions(self):
        instructions = [
            "LMB: Place Block/Change Movability/Place Teleport",
            "RMB: Remove Object",
            "1, 2, 3: Place Player, Key, Door",
            "T: Toggle Teleport Placement",
            "S: Save Level"
        ]
        font = pygame.font.SysFont("monospace", 14)
        for i, instruction in enumerate(instructions):
            instruction_text = font.render(instruction, True, Color.WHITE)
            self.screen.screen.blit(instruction_text, (10, 3 + i * 15))

    def draw_dropdown_menu(self):
        font = pygame.font.SysFont("monospace", 18)
        pygame.draw.rect(self.screen.screen, Color.DARK_GRAY, self.dropdown_rect)
        
        if self.selected_level_index is not None:
            dropdown_text = font.render(f"Level {self.selected_level_index + 1}", True, Color.WHITE)
        else:
            dropdown_text = font.render("Select Level", True, Color.WHITE)
        
        text_rect = dropdown_text.get_rect(center=self.dropdown_rect.center)
        self.screen.screen.blit(dropdown_text, text_rect.topleft)
        
        if self.dropdown_open:
            for i, rect in enumerate(self.dropdown_items):
                color = Color.GREEN if i == self.selected_level_index else Color.DARK_GRAY
                pygame.draw.rect(self.screen.screen, color, rect)
                item_text = font.render(f"Level {i + 1}", True, Color.WHITE)
                self.screen.screen.blit(item_text, rect.topleft)

    def add_teleport_pair(self, x1, y1, x2, y2):
        teleport_pair = TeleportPair(x1, y1, x2, y2, self.block_size, self.block_size)
        self.teleports.append(teleport_pair)

    def draw_elements(self):
        logging.debug("Drawing elements on screen")
        self.screen.refresh_background()
        for block in self.blocks:
            block.draw(self.screen.screen)
        if self.player_start:
            self.player_start.draw(self.screen.screen)
        if self.key_start:
            self.key_start.draw(self.screen.screen)
        if self.door_start:
            self.door_start.draw(self.screen.screen)
        if self.teleports:
            for teleport in self.teleports:
                teleport.draw(self.screen.screen)
        self.draw_dropdown_menu()
        self.draw_instructions()
        pygame.display.flip()

    def remove_object(self, x, y):
        for block in self.blocks:
            if block.rect.collidepoint(x, y):
                self.blocks.remove(block)
                logging.info(f"Removed block at ({x}, {y})")
                break
        if self.player_start and self.player_start.rect.collidepoint(x, y):
            self.history.append(('player', self.player_start))
            self.player_start = None
            logging.info("Removed player start position")
        if self.key_start and self.key_start.rect.collidepoint(x, y):
            self.history.append(('key', self.key_start))
            self.key_start = None
            logging.info("Removed key start position")
        if self.door_start and self.door_start.rect.collidepoint(x, y):
            self.history.append(('door', self.door_start))
            self.door_start = None
            logging.info("Removed door start position")
        if self.teleports:
            for teleport in self.teleports:
                if teleport.teleport1.rect.collidepoint(x, y) or teleport.teleport2.rect.collidepoint(x, y):
                    self.history.append(('teleport', teleport))
                    self.teleports.remove(teleport)
                    logging.info("Removed teleport pair")
                    return

    def run(self):
        logging.info("Starting LevelEditor run loop")
        running = True
        redraw_needed = True  # Flag to track if redraw is needed
        placing_teleport = False
        teleport_start_pos = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.info("Received QUIT event")
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    logging.info(f"Mouse button down at position: {event.pos}")
                    if self.return_button_rect.collidepoint(event.pos):
                        logging.info("Return button clicked")
                        running = False
                    elif self.dropdown_rect.collidepoint(event.pos):
                        self.dropdown_open = not self.dropdown_open
                        logging.info(f"Dropdown menu {'opened' if self.dropdown_open else 'closed'}")
                        redraw_needed = True
                    elif self.dropdown_open:
                        for i, rect in enumerate(self.dropdown_items):
                            if rect.collidepoint(event.pos):
                                self.selected_level_index = i
                                self.load_level(i)
                                self.dropdown_open = False
                                logging.info(f"Selected level {i}")
                                redraw_needed = True
                                break
                    else:
                        x, y = event.pos
                        x = (x // self.block_size) * self.block_size
                        y = (y // self.block_size) * self.block_size
                        if event.button == 1:  # Left click to place block or teleport
                            if placing_teleport:
                                if teleport_start_pos is None:
                                    teleport_start_pos = (x, y)
                                    logging.info(f"Teleport start position set at ({x}, {y})")
                                else:
                                    self.add_teleport_pair(teleport_start_pos[0], teleport_start_pos[1], x, y)
                                    logging.info(f"Placed teleport pair from ({teleport_start_pos[0]}, {teleport_start_pos[1]}) to ({x}, {y})")
                                    teleport_start_pos = None
                                    placing_teleport = False
                                redraw_needed = True
                            else:
                                for block in self.blocks:
                                    if block.rect.collidepoint(x, y):
                                        block.change_movability()
                                        logging.info(f"Changed movability of block at ({x}, {y})")
                                        break
                                else:
                                    new_block = Block(x, y, self.block_size, self.block_size)
                                    self.blocks.append(new_block)
                                    logging.info(f"Placed new block at ({x}, {y})")
                                redraw_needed = True
                        elif event.button == 3:  # Right click to remove object
                            self.remove_object(x, y)
                            redraw_needed = True
                elif event.type == pygame.KEYDOWN:
                    x, y = pygame.mouse.get_pos()
                    x = (x // self.block_size) * self.block_size
                    y = (y // self.block_size) * self.block_size
                    if event.key == pygame.K_1:  # Press '1' to place player
                        self.player_start = Player(x, y, self.block_size, self.block_size)
                        logging.info(f"Placed player start at ({x}, {y})")
                        redraw_needed = True
                    elif event.key == pygame.K_2:  # Press '2' to place key
                        self.key_start = Key(x, y, self.block_size, self.block_size)
                        logging.info(f"Placed key start at ({x}, {y})")
                        redraw_needed = True
                    elif event.key == pygame.K_3:  # Press '3' to place door
                        self.door_start = Door(x, y, self.block_size, self.block_size)
                        logging.info(f"Placed door start at ({x}, {y})")
                        redraw_needed = True
                    elif event.key == pygame.K_t:  # Press 'T' to toggle teleport placement mode
                        placing_teleport = not placing_teleport
                        teleport_start_pos = None
                        logging.info(f"Teleport placement mode {'enabled' if placing_teleport else 'disabled'}")
                    elif event.key == pygame.K_s:  # Press 's' to save the level
                        self.save_level()
                    elif event.key == pygame.K_z:  # Press 'z' to undo the last action
                        self.undo_last_action()
                        redraw_needed = True
                    elif event.key == pygame.K_ESCAPE:
                        logging.info("Return button clicked")
                        running = False

            if redraw_needed:
                self.draw_elements()
                redraw_needed = False
        self.screen.display_menu()