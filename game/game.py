import pygame
import time
import logging
from game.key import Key
from game.door import Door
from game.block import Block
from game.player import Player
from game.screen import Screen
from game.levels import create_levels
from game.leveleditor import LevelEditor

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class Game:
    def __init__(self):
        logging.info("Initializing game")
        self.state = "not_started"
        self.screen = Screen()
        self.current_level_index = 0
        self.total_moves = 0
        self.total_undos = 0
        self.total_resets = 0
        self.start_time = None
        self.levels = create_levels()
        self.load_level(self.current_level_index)

    def load_level(self, level_index):
        logging.info(f"Loading level {level_index + 1}")
        level = self.levels[level_index]
        self.player = Player(level.player_start[0], level.player_start[1], self.screen.block_size, self.screen.block_size)
        self.key = Key(level.key_start[0], level.key_start[1], self.screen.block_size, self.screen.block_size)
        self.door = Door(level.door_start[0], level.door_start[1], self.screen.block_size, self.screen.block_size)
        self.blocks = level.blocks
        self.initial_player_pos = level.player_start
        self.initial_key_pos = level.key_start
        self.initial_door_pos = level.door_start
        self.initial_block_positions = {block: (block.rect.x, block.rect.y) for block in self.blocks}

    def reset_game(self):
        logging.info("Resetting game")
        self.player.movements = []
        self.key.movements = []
        self.door.movements = []
        self.player.rect.topleft = self.initial_player_pos
        self.key.rect.topleft = self.initial_key_pos
        self.door.rect.topleft = self.initial_door_pos
        for block in self.blocks:
            block.rect.topleft = self.initial_block_positions[block]
            block.movements = []
        self.total_moves = 0
        self.total_undos = 0
        self.total_resets = 0
        self.door.open = False
        self.door.change_image()
        self.total_resets += 1
        self.state = "in_progress"

    def start_game(self):
        logging.info("Starting game")
        self.state = "in_progress"
        self.current_level_index = 0
        self.load_level(self.current_level_index)
        self.start_time = time.time()

    def end_game(self):
        logging.info("Ending game")
        self.current_level_index = 0
        self.state = "ended"

    def win_game(self):
        logging.info("Winning game")
        self.state = "won"
        self.elapsed_time = time.time() - self.start_time

    def get_state(self):
        return self.state
    
    def shake_if_colliding(self, obj1_pos, obj2_pos, obj1, obj2, obj1_name, obj2_name):
        if obj1_pos == obj2_pos:
            logging.warning(f"{obj1_name} and {obj2_name} are about to collide")
            obj1.shake(self.screen.screen)
            obj2.shake(self.screen.screen)
    
    def undo_last_action(self):
        logging.info("Undoing last action")
        new_player_pos = (self.player.rect.x, self.player.rect.y)
        new_key_pos = (self.key.rect.x, self.key.rect.y)
        new_door_pos = (self.door.rect.x, self.door.rect.y)
        new_block_positions = {block: (block.rect.x, block.rect.y) for block in self.blocks}
        if self.player.movements:
            last_player_move = self.player.movements[-1]
            new_player_pos = (self.player.rect.x - last_player_move[0], self.player.rect.y - last_player_move[1])
        if self.key.movements:
            last_key_move = self.key.movements[-1]
            new_key_pos = (self.key.rect.x - last_key_move[0], self.key.rect.y - last_key_move[1])
        if self.door.movements:
            last_door_move = self.door.movements[-1]
            new_door_pos = (self.door.rect.x - last_door_move[0], self.door.rect.y - last_door_move[1])
        for block in self.blocks:
            if block.movements:
                last_block_move = block.movements[-1]
                new_block_positions[block] = (block.rect.x - last_block_move[0], block.rect.y - last_block_move[1])
        self.total_undos += 1

        player_not_colliding = (
            new_player_pos != new_key_pos and
            new_player_pos != new_door_pos and
            not any(new_player_pos == new_block_pos for new_block_pos in new_block_positions.values())
        )
        key_not_colliding = (
            new_key_pos != new_door_pos and
            not any(new_key_pos == new_block_pos for new_block_pos in new_block_positions.values())
        )
        door_not_colliding = (
            not any(new_door_pos == new_block_pos for new_block_pos in new_block_positions.values())
        )
        blocks_not_colliding = (
            not any(new_block_pos == other_block_pos for block, new_block_pos in new_block_positions.items() for other_block, other_block_pos in new_block_positions.items() if block != other_block)
        )
        logging.info(f"Player not colliding: {player_not_colliding}, Key not colliding: {key_not_colliding}, Door not colliding: {door_not_colliding}, Blocks not colliding: {blocks_not_colliding}")
        if player_not_colliding and key_not_colliding and door_not_colliding and blocks_not_colliding:
            self.player.undo_movement()
            self.key.undo_movement()
            self.door.undo_movement()
            for block in self.blocks:
                block.undo_movement()
            self.total_undos += 1
        else:
            self.shake_if_colliding(new_player_pos, new_key_pos, self.player, self.key, "Player", "Key")
            self.shake_if_colliding(new_player_pos, new_door_pos, self.player, self.door, "Player", "Door")
            self.shake_if_colliding(new_key_pos, new_door_pos, self.key, self.door, "Key", "Door")
            if new_player_pos == new_key_pos == new_door_pos:
                logging.warning("Player, key, and door are about to collide")
                self.player.shake(self.screen.screen)
                self.key.shake(self.screen.screen)
                self.door.shake(self.screen.screen)
            for block, new_block_pos in new_block_positions.items():
                self.shake_if_colliding(new_block_pos, new_player_pos, block, self.player, "Block", "Player")
                self.shake_if_colliding(new_block_pos, new_key_pos, block, self.key, "Block", "Key")
                self.shake_if_colliding(new_block_pos, new_door_pos, block, self.door, "Block", "Door")
                if new_block_pos == new_player_pos == new_key_pos:
                    logging.warning("Block, player, and key are about to collide")
                    block.shake(self.screen.screen)
                    self.player.shake(self.screen.screen)
                    self.key.shake(self.screen.screen)
                if new_block_pos == new_player_pos == new_door_pos:
                    logging.warning("Block, player, and door are about to collide")
                    block.shake(self.screen.screen)
                    self.player.shake(self.screen.screen)
                    self.door.shake(self.screen.screen)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Received QUIT event")
                self.end_game()
            elif event.type == pygame.KEYDOWN:
                logging.info(f"Key pressed: {pygame.key.name(event.key)}")
                if event.key == pygame.K_w:
                    self.player.move(0, -self.screen.block_size, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks)
                    self.total_moves += 1
                elif event.key == pygame.K_s:
                    self.player.move(0, self.screen.block_size, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks)
                    self.total_moves += 1
                elif event.key == pygame.K_a:
                    self.player.move(-self.screen.block_size, 0, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks)
                    self.total_moves += 1
                elif event.key == pygame.K_d:
                    self.player.move(self.screen.block_size, 0, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks)
                    self.total_moves += 1
                elif event.key == pygame.K_z:
                    logging.info("Undoing last move")
                    self.undo_last_action()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.reset_game()
                    self.state = "not_started"

            if self.key.rect.colliderect(self.door.rect):
                logging.info("Key and door collided")
                self.door.open_door()
                self.door.change_image()
                self.key.delete_key()
            
            # Player win condition
            if self.player.rect.colliderect(self.door.rect):
                logging.info("Player and door collided")
                self.current_level_index += 1
                if self.current_level_index < len(self.levels):
                    logging.info(f"Loading next level: {self.current_level_index}")
                    self.load_level(self.current_level_index)
                else:
                    logging.info("No more levels to load")
                    self.win_game()


    def handle_menu_events(self, start_rect, edit_rect, quit_rect):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Received QUIT event in menu")
                self.end_game()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                logging.info(f"Mouse button down at position: {event.pos}")
                if start_rect.collidepoint(event.pos):
                    logging.info("Start button clicked")
                    self.start_game()
                    return True
                elif edit_rect.collidepoint(event.pos):
                    logging.info("Edit button clicked")
                    editor = LevelEditor(self.screen)
                    editor.run()
                    self.levels = create_levels()
                elif quit_rect.collidepoint(event.pos):
                    logging.info("Quit button clicked")
                    self.end_game()
                    return False
        return True
    
    def handle_winning_screen_events(self, return_rect):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Received QUIT event on winning screen")
                self.end_game()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logging.info(f"Mouse button down at position: {event.pos}")
                if return_rect.collidepoint(event.pos):
                    logging.info("Return button clicked on winning screen")
                    return True
        return False

    def run(self):
        while True:
            while self.get_state() == "not_started":
                start_rect, edit_rect, quit_rect = self.screen.display_menu()
                while self.get_state() == "not_started":
                    if not self.handle_menu_events(start_rect, edit_rect, quit_rect):
                        logging.info("Exiting game from menu")
                        pygame.quit()
                        return
                
            while self.get_state() == "in_progress":
                self.handle_events()
                self.screen.update_screen(self.player, self.key, self.door, self.blocks, self.current_level_index + 1)
            
            if self.get_state() == "ended":
                logging.info("Game ended, resetting game")
                self.reset_game()
                self.state = "not_started"
            
            if self.get_state() == "won":
                return_rect = self.screen.display_winning_screen(self.total_moves, self.total_undos, self.total_resets, self.elapsed_time)
                while not self.handle_winning_screen_events(return_rect):
                    pygame.time.wait(100)  # Wait for 100 milliseconds before checking again
                self.reset_game()
                self.state = "not_started"