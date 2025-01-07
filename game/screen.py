import pygame
import logging
import sys
from game.color import Color

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Screen:
    def __init__(self, width=880, height=880, background_color=Color.BLACK, font_type="monospace", font_size=15):
        logging.info("Initializing screen")
        self.width = width
        self.height = height
        self.background_color = background_color
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont(font_type, font_size)
        self.grid_size = 10
        self.block_size = min(width, height) // (self.grid_size + 1)
        pygame.display.set_caption("Puzzle Game")

    def refresh_background(self):
        self.screen.fill(self.background_color)
        self.draw_border()

    def draw_border(self):
        for x in range(self.grid_size + 1):
            for y in range(self.grid_size + 1):
                if x == 0 or x == self.grid_size or y == 0 or y == self.grid_size:
                    rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    pygame.draw.rect(self.screen, Color.DARK_GRAY, rect)

    def draw_player(self, player):
        player.draw(self.screen)

    def draw_key(self, key):
        key.draw(self.screen)

    def draw_door(self, door):
        door.draw(self.screen)

    def draw_blocks(self, blocks):
        for block in blocks:
            block.draw(self.screen)

    def draw_teleports(self, teleports):
        for teleport in teleports:
            teleport.draw(self.screen)

    def draw_level_text(self, level, max_level):
        level_font = pygame.font.SysFont("monospace", 25)
        level_text = level_font.render(f"Level {level}/{max_level}", True, Color.GREEN)
        text_rect = level_text.get_rect(center=(self.width // 2, 35))
        self.screen.blit(level_text, text_rect)

    def draw_instructions(self):
        instructions = [
            "WASD for movement",
            "Z to undo movement",
            "R to reset the level",
            "ESC to return to menu"
        ]
        for i, instruction in enumerate(instructions):
            instruction_text = self.font.render(instruction, True, Color.WHITE)
            self.screen.blit(instruction_text, (10, 2 + i * 20))

    def update_screen(self, player, key, door, blocks, teleports, level, max_level):
        self.refresh_background()
        self.draw_teleports(teleports)
        self.draw_player(player)
        self.draw_key(key)
        self.draw_door(door)
        self.draw_blocks(blocks)
        self.draw_level_text(level, max_level)
        self.draw_instructions()
        pygame.display.update()

    def display_challenge_menu(self, current_index):
        menu_font = pygame.font.SysFont("monospace", 40)
        arrow_font = pygame.font.SysFont("monospace", 60)
        self.screen.fill(Color.BLACK)
        left_arrow = arrow_font.render("<", True, Color.WHITE)
        right_arrow = arrow_font.render(">", True, Color.WHITE)
        challenge_name = menu_font.render(f"Challenge {current_index}", True, Color.WHITE)

        left_rect = left_arrow.get_rect(center=(self.width // 4, self.height // 2))
        middle_rect = challenge_name.get_rect(center=(self.width // 2, self.height // 2))
        right_rect = right_arrow.get_rect(center=(3 * self.width // 4, self.height // 2))

        self.screen.blit(left_arrow, left_rect)
        self.screen.blit(challenge_name, middle_rect)
        self.screen.blit(right_arrow, right_rect)
        pygame.display.update()
        return left_rect, middle_rect, right_rect

    def display_menu(self):
        logging.info("Displaying menu")
        menu_font = pygame.font.SysFont("monospace", 50)
        start_text = menu_font.render("Start", True, Color.WHITE)
        start_rect = start_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
        challenge_text = menu_font.render("Challenges", True, Color.WHITE)
        challenge_rect = challenge_text.get_rect(center=(self.width // 2, self.height // 2))


        self.screen.fill(Color.BLACK)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(challenge_text, challenge_rect)

        if sys.platform != "emscripten":
            edit_text = menu_font.render("Editor", True, Color.WHITE)
            edit_rect = edit_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(edit_text, edit_rect)
        else:
            edit_rect = None

        continue_rect = None
        if sys.platform == "emscripten":
            from js import window
            saved_level = window.localStorage.getItem("current_level_index")
            if saved_level is not None:
                continue_text = menu_font.render("Continue", True, Color.WHITE)
                continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
                self.screen.blit(continue_text, continue_rect)

        pygame.display.update()
        logging.debug("Menu displayed with Start, Continue (if available), and Edit options")
        return start_rect, edit_rect, continue_rect, challenge_rect
    
    def display_winning_screen(self, total_moves, total_undos, total_resets, elapsed_time):
        logging.info("Displaying winning screen")
        winning_font = pygame.font.SysFont("monospace", 50)
        moves_text = winning_font.render(f"Total Moves: {total_moves}", True, Color.WHITE)
        undos_text = winning_font.render(f"Total Undos: {total_undos}", True, Color.WHITE)
        resets_text = winning_font.render(f"Total Resets: {total_resets}", True, Color.WHITE)
        win_text = winning_font.render("You Win!", True, Color.GREEN)
        return_text = winning_font.render("Return to Menu", True, Color.WHITE)
        time_text = winning_font.render(f"Time: {int(elapsed_time)} seconds", True, Color.WHITE)

        win_rect = win_text.get_rect(center=(self.width // 2, self.height // 2 - 200))
        time_rect = time_text.get_rect(center=(self.width // 2, self.height // 2 - 150))
        moves_rect = moves_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
        undos_rect = undos_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        resets_rect = resets_text.get_rect(center=(self.width // 2, self.height // 2))
        return_rect = return_text.get_rect(center=(self.width // 2, self.height // 2 + 100))

        self.screen.fill(Color.BLACK)
        self.screen.blit(win_text, win_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(moves_text, moves_rect)
        self.screen.blit(undos_text, undos_rect)
        self.screen.blit(resets_text, resets_rect)
        self.screen.blit(return_text, return_rect)
        pygame.display.update()
        logging.debug("Winning screen displayed with total moves, undos, resets, and elapsed time")
        return return_rect