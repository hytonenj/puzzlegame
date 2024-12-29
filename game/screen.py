from game.color import Color
import pygame

class Screen:
    def __init__(self, width=800, height=800, background_color=Color.BLACK, font_type="monospace", font_size=15):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont(font_type, font_size)
        self.grid_size = 9
        self.block_size = min(width, height) // (self.grid_size + 1)

    def refresh_background(self):
        self.screen.fill(self.background_color)
        self.draw_border()

    def draw_border(self):
        for x in range(self.grid_size + 1):
            for y in range(self.grid_size + 1):
                if x == 0 or x == self.grid_size or y == 0 or y == self.grid_size:
                    rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                    pygame.draw.rect(self.screen, Color.GRAY, rect)

    def draw_player(self, player):
        player.draw(self.screen)

    def draw_key(self, key):
        key.draw(self.screen)

    def draw_door(self, door):
        door.draw(self.screen)

    def draw_blocks(self, blocks):
        for block in blocks:
            block.draw(self.screen)

    def draw_level_text(self, level):
        level_text = self.font.render(f"Level {level}", True, Color.WHITE)
        self.screen.blit(level_text, (10, 2))

    def draw_instructions(self):
        instructions = [
            "WASD for movement",
            "Z to undo movement",
            "R to reset the level"
        ]
        for i, instruction in enumerate(instructions):
            instruction_text = self.font.render(instruction, True, Color.WHITE)
            self.screen.blit(instruction_text, (10, 20 + i * 20))

    def update_screen(self, player, key, door, blocks, level):
        self.refresh_background()
        self.draw_player(player)
        self.draw_key(key)
        self.draw_door(door)
        self.draw_blocks(blocks)
        self.draw_level_text(level)
        self.draw_instructions()
        pygame.display.update()


    def display_menu(self):
        menu_font = pygame.font.SysFont("monospace", 50)
        start_text = menu_font.render("Start", True, Color.WHITE)
        quit_text = menu_font.render("Quit", True, Color.WHITE)

        start_rect = start_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 50))

        self.screen.fill(Color.BLACK)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(quit_text, quit_rect)
        pygame.display.update()

        return start_rect, quit_rect
    
    def display_winning_screen(self, total_moves, total_undos, total_resets, elapsed_time):
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

        return return_rect