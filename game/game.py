import pygame
import time
import logging
import asyncio
import sys
from game.key import Key
from game.door import Door
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
        self.running = True
        self.challenge = False
        self.levels_path = "../data/levels.json"

    def load_level(self, level_index):
        logging.info(f"Loading level {level_index + 1}")
        self.levels = create_levels(self.levels_path)
        level = self.levels[level_index]
        self.player = Player(level.player_start[0], level.player_start[1], self.screen.block_size, self.screen.block_size)
        self.key = Key(level.key_start[0], level.key_start[1], self.screen.block_size, self.screen.block_size)
        self.door = Door(level.door_start[0], level.door_start[1], self.screen.block_size, self.screen.block_size)
        self.blocks = level.blocks
        self.teleports = level.teleports
        self.initial_player_pos = level.player_start
        self.initial_key_pos = level.key_start
        self.initial_door_pos = level.door_start
        self.initial_block_positions = {block: (block.rect.x, block.rect.y) for block in level.blocks}
        self.save_current_level()
    
    def save_current_level(self):
        if self.challenge:
            return
        if sys.platform == "emscripten":
            logging.info(f"Saving current level: {self.current_level_index}")
            from js import window
            window.localStorage.setItem("current_level_index", str(self.current_level_index))
            window.localStorage.setItem("total_moves", str(self.total_moves))
            window.localStorage.setItem("total_undos", str(self.total_undos))
            window.localStorage.setItem("total_resets", str(self.total_resets))
            self.elapsed_time = time.time() - self.start_time
            window.localStorage.setItem("elapsed_time", str(self.elapsed_time))
            logging.info("Current level and game state saved")
        else:
            logging.info("Saving levels is only supported in the browser")

    def load_saved_level(self):
        if sys.platform == "emscripten":
            from js import window
            saved_level = window.localStorage.getItem("current_level_index")
            if saved_level is not None:
                self.current_level_index = int(saved_level)
                self.total_moves = int(window.localStorage.getItem("total_moves"))
                self.total_undos = int(window.localStorage.getItem("total_undos"))
                self.total_resets = int(window.localStorage.getItem("total_resets"))
                self.elapsed_time = float(window.localStorage.getItem("elapsed_time"))
                self.start_time = time.time() - self.elapsed_time
                self.load_level(self.current_level_index)

    def reset_level(self):
        logging.info("Resetting level")
        self.player.movements = []
        self.key.movements = []
        self.door.movements = []
        self.player.rect.topleft = self.initial_player_pos
        self.key.rect.topleft = self.initial_key_pos
        self.door.rect.topleft = self.initial_door_pos
        for block in self.blocks:
            block.rect.topleft = self.initial_block_positions[block]
            block.movements = []
        self.door.open = False
        self.door.change_image()
        self.state = "in_progress"

    def reset_game(self):
        logging.info("Resetting game")
        self.challenge = False
        self.reset_level()
        self.total_moves = 0
        self.total_undos = 0
        self.total_resets = 0

    def start_game(self, level_index):
        logging.info("Starting game")
        self.start_time = time.time()
        self.state = "in_progress"
        self.current_level_index = level_index
        self.load_level(self.current_level_index)

    def continue_game(self):
        logging.info("Continuing game")
        self.start_time = time.time()
        self.state = "in_progress"
        self.load_saved_level()

    def end_game(self):
        logging.info("Ending game")
        self.current_level_index = 0
        self.state = "ended"

    def win_game(self):
        logging.info("Winning game")
        self.state = "won"
        self.elapsed_time = time.time() - self.start_time
        # Remove the saved level from browser storage
        if sys.platform == "emscripten" and not self.challenge:
            from js import window
            window.localStorage.removeItem("current_level_index")

    def get_state(self):
        return self.state
    
    async def shake_if_colliding(self, obj1_pos, obj2_pos, obj1, obj2, obj1_name, obj2_name):
        if obj1_pos == obj2_pos:
            logging.warning(f"{obj1_name} and {obj2_name} are about to collide")
            await asyncio.gather(
                obj1.shake(self.screen.screen),
                obj2.shake(self.screen.screen)
            )
    
    async def undo_last_action(self):
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

        player_within_bounds = self.is_within_bounds(new_player_pos[0], new_player_pos[1])
        key_within_bounds = self.is_within_bounds(new_key_pos[0], new_key_pos[1])
        door_within_bounds = self.is_within_bounds(new_door_pos[0], new_door_pos[1])
        blocks_within_bounds = all(self.is_within_bounds(pos[0], pos[1]) for pos in new_block_positions.values())

        def can_move_through_teleport(obj, new_pos):
            for teleport_pair in self.teleports:
                if teleport_pair.can_move_through_teleport(obj, new_pos, self.blocks + [self.key, self.door], self.screen.grid_size, self.screen.block_size):
                    return True
            return False

        player_not_colliding = (
            can_move_through_teleport(self.player, new_player_pos) or 
            (
                new_player_pos != new_key_pos and
                new_player_pos != new_door_pos and
                not any(new_player_pos == new_block_pos for new_block_pos in new_block_positions.values())
            )
        )

        key_not_colliding = (
            can_move_through_teleport(self.key, new_key_pos) or
            not any(new_key_pos == new_block_pos for new_block_pos in new_block_positions.values())
        )

        door_not_colliding = (
            can_move_through_teleport(self.door, new_door_pos) or
            not any(new_door_pos == new_block_pos for new_block_pos in new_block_positions.values())
        )

        blocks_not_colliding = (
            all(can_move_through_teleport(block, new_block_pos) for block, new_block_pos in new_block_positions.items()) or
            not any(new_block_pos == other_block_pos for block, new_block_pos in new_block_positions.items() for other_block, other_block_pos in new_block_positions.items() if block != other_block)
        )
        logging.debug(f"Player not colliding: {player_not_colliding}, Key not colliding: {key_not_colliding}, Door not colliding: {door_not_colliding}, Blocks not colliding: {blocks_not_colliding}")
        logging.debug(f"Player within bounds: {player_within_bounds}, Key within bounds: {key_within_bounds}, Door within bounds: {door_within_bounds}, Blocks within bounds: {blocks_within_bounds}")
        if (player_not_colliding and key_not_colliding and door_not_colliding and blocks_not_colliding
            and player_within_bounds and key_within_bounds and door_within_bounds and blocks_within_bounds):
            player_dx, player_dy = self.player.undo_movement()
            key_dx, key_dy = self.key.undo_movement()
            door_dx, door_dy = self.door.undo_movement()
            block_movements = []
            for block in self.blocks:
                block_dx, block_dy = block.undo_movement()
                block_movements.append((block, block_dx, block_dy))
            # Check for teleport collisions after undoing movements
            all_objects = self.blocks + [self.key, self.door, self.player]
            no_key_door_objects = self.blocks + [self.player]
            self._check_teleport_collision(self.teleports, player_dx, player_dy, all_objects, self.player, self.screen.grid_size, self.screen.block_size)
            self._check_teleport_collision(self.teleports, key_dx, key_dy, no_key_door_objects, self.key, self.screen.grid_size, self.screen.block_size)
            self._check_teleport_collision(self.teleports, door_dx, door_dy, no_key_door_objects, self.door, self.screen.grid_size, self.screen.block_size)
            for block, block_dx, block_dy in block_movements:
                self._check_teleport_collision(self.teleports, block_dx, block_dy, all_objects, block, self.screen.grid_size, self.screen.block_size)
        else:
            await self.shake_if_colliding(new_player_pos, new_key_pos, self.player, self.key, "Player", "Key")
            await self.shake_if_colliding(new_player_pos, new_door_pos, self.player, self.door, "Player", "Door")
            for block, new_block_pos in new_block_positions.items():
                await self.shake_if_colliding(new_block_pos, new_player_pos, block, self.player, "Block", "Player")
                await self.shake_if_colliding(new_block_pos, new_key_pos, block, self.key, "Block", "Key")
                await self.shake_if_colliding(new_block_pos, new_door_pos, block, self.door, "Block", "Door")
            await self.shake_if_out_of_bounds(new_player_pos, self.player, "Player")
            await self.shake_if_out_of_bounds(new_key_pos, self.key, "Key")
            await self.shake_if_out_of_bounds(new_door_pos, self.door, "Door")
            for block, new_block_pos in new_block_positions.items():
                await self.shake_if_out_of_bounds(new_block_pos, block, "Block")

    def is_within_bounds(self, x, y):
        return self.screen.block_size <= x < self.screen.grid_size * self.screen.block_size and self.screen.block_size <= y < self.screen.grid_size * self.screen.block_size

    async def shake_if_out_of_bounds(self, new_pos, obj, obj_name):
        if not self.is_within_bounds(new_pos[0], new_pos[1]):
            logging.warning(f"{obj_name} is out of bounds")
            await obj.shake(self.screen.screen)

    def _check_teleport_collision(self, teleports, dx, dy, objects, obj, grid_size, block_size):
        for teleport_pair in teleports:
            teleport_pair.check_and_teleport(obj, dx, dy, objects, grid_size, block_size)
    
    async def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Received QUIT event")
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                logging.info(f"Key pressed: {pygame.key.name(event.key)}")
                if event.key == pygame.K_w:
                    self.player.move(0, -self.screen.block_size, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks, self.teleports)
                    self.total_moves += 1
                    self.save_current_level()
                elif event.key == pygame.K_s:
                    self.player.move(0, self.screen.block_size, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks, self.teleports)
                    self.total_moves += 1
                    self.save_current_level()
                elif event.key == pygame.K_a:
                    self.player.move(-self.screen.block_size, 0, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks, self.teleports)
                    self.total_moves += 1
                    self.save_current_level()
                elif event.key == pygame.K_d:
                    self.player.move(self.screen.block_size, 0, self.screen.grid_size, self.screen.block_size, self.key, self.door, self.blocks, self.teleports)
                    self.total_moves += 1
                    self.save_current_level()
                elif event.key == pygame.K_z:
                    await self.undo_last_action()
                    self.total_undos += 1
                    self.save_current_level()
                elif event.key == pygame.K_r:
                    self.reset_level()
                    self.total_resets += 1
                    self.save_current_level()
                elif event.key == pygame.K_ESCAPE:
                    self.save_current_level()
                    self.reset_game()
                    self.state = "not_started"

            if self.key.rect.colliderect(self.door.rect):
                logging.info("Key and door collided")
                self.door.open_door()
                self.door.change_image()
                self.key.delete_key()
            
            # Player win condition
            if self.player.rect.colliderect(self.door.rect) and self.door.open:
                logging.info("Player and door collided")
                self.current_level_index += 1
                if self.challenge:
                    logging.info("Level completed")
                    self.state = "challenge_menu"
                    self.win_game()
                elif self.current_level_index < len(self.levels):
                    self.load_level(self.current_level_index)
                else:
                    logging.info("No more levels to load")
                    self.win_game()

    def handle_menu_events(self, start_rect, edit_rect, continue_rect, challenge_rect):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Received QUIT event in menu")
                self.running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                logging.info(f"Mouse button down at position: {event.pos}")
                if start_rect.collidepoint(event.pos):
                    logging.info("Start button clicked")
                    self.start_game(level_index=0)
                    return True
                elif challenge_rect and challenge_rect.collidepoint(event.pos):
                    logging.info("Levels button clicked")
                    self.state = "challenge_menu"
                    return True
                elif edit_rect and edit_rect.collidepoint(event.pos):
                    logging.info("Edit button clicked")
                    editor = LevelEditor(self.screen)
                    editor.run()
                    self.levels = create_levels(self.levels_path)
                elif continue_rect and continue_rect.collidepoint(event.pos):
                    logging.info("Continue button clicked")
                    self.continue_game()
                    return True
        return True
    
    async def handle_challenge_events(self):
        current_index = 0
        self.levels = create_levels(self.levels_path)
        left_rect, middle_rect, right_rect = self.screen.display_challenge_menu(current_index)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.info("Received QUIT event in Levels")
                    self.running = False
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        logging.info("Return button clicked")
                        self.state = "not_started"
                        return False
                    elif event.key == pygame.K_RIGHT:
                        current_index = (current_index + 1) % len(self.levels)
                    elif event.key == pygame.K_LEFT:
                        current_index = (current_index - 1) % len(self.levels)
                    left_rect, middle_rect, right_rect = self.screen.display_challenge_menu(current_index)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    logging.info(f"Mouse button down at position: {event.pos}")
                    if left_rect.collidepoint(event.pos):
                        current_index = (current_index - 1) % len(self.levels)
                        left_rect, middle_rect, right_rect = self.screen.display_challenge_menu(current_index)
                    elif right_rect.collidepoint(event.pos):
                        current_index = (current_index + 1) % len(self.levels)
                        left_rect, middle_rect, right_rect = self.screen.display_challenge_menu(current_index)
                    elif middle_rect.collidepoint(event.pos):
                        logging.info(f"Level {current_index} selected")
                        self.state = "in_progress"
                        self.challenge = True
                        self.start_game(current_index)
                        return True
            await asyncio.sleep(0)
        return True
        
    async def handle_winning_screen_events(self, return_rect):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logging.info("Received QUIT event on winning screen")
                    self.end_game()
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse button
                    logging.info(f"Left mouse button down at position: {event.pos}")
                    if return_rect.collidepoint(event.pos):
                        logging.info("Return button clicked on winning screen")
                        return True
            await asyncio.sleep(0)

    async def run(self):
        while self.running:
            while self.get_state() == "not_started":
                start_rect, edit_rect, continue_rect, challenge_rect = self.screen.display_menu()
                while self.get_state() == "not_started":
                    if not self.handle_menu_events(start_rect, edit_rect, continue_rect, challenge_rect):
                        logging.info("Exiting game from menu")
                        return  # Exit the run function
                    await asyncio.sleep(0)

            while self.get_state() == "in_progress":
                await self.handle_events()
                self.screen.update_screen(self.player, self.key, self.door, self.blocks, self.teleports, self.current_level_index + 1, len(self.levels))
                if not self.running:
                    logging.info("Exiting game from in progress")
                    return
                await asyncio.sleep(0)

            if self.get_state() == "ended":
                logging.info("Game ended, resetting game")
                self.reset_game()
                self.state = "not_started"

            if self.get_state() == "won":
                return_rect = self.screen.display_winning_screen(self.total_moves, self.total_undos, self.total_resets, self.elapsed_time)
                while self.running:
                    if await self.handle_winning_screen_events(return_rect):
                        self.reset_game()
                        self.state = "not_started"
                        break

            if self.get_state() == "challenge_menu":
                await self.handle_challenge_events()