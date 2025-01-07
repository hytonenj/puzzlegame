import pygame
import logging
import asyncio

class Player:
    def __init__(self, x, y, width, height, image_path="assets/pixel_player.png"):
        self.movements = []
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def move(self, dx, dy, grid_size, block_size, key=None, door=None, blocks=[], teleports=[]):
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        if not self._is_within_bounds(new_x, new_y, grid_size, block_size, door):
            return

        if self._handle_block_collisions(new_x, new_y, dx, dy, grid_size, block_size, key, door, blocks, teleports):
            return

        if self._handle_key_movement(dx, dy, block_size, grid_size, key, door, blocks, teleports):
            return

        if self._handle_door_movement(dx, dy, block_size, grid_size, door, blocks, teleports):
            return

        self.rect.x = new_x
        self.rect.y = new_y
        self.record_movement((dx, dy))
        self._check_teleport_collision(teleports, dx, dy, blocks + [key, door], grid_size, block_size, obj=None)

    def _is_within_bounds(self, x, y, grid_size, block_size, door):
        return (block_size <= x < grid_size * block_size and block_size <= y < grid_size * block_size) or (door and door.open and door.rect.collidepoint(x, y))

    def _is_teleport_location_free(self, x, y, dx, dy, teleports, objects):
        for teleport_pair in teleports:
            if teleport_pair.teleport1.rect.collidepoint(x, y):
                if not teleport_pair.teleport1.is_location_free(dx, dy, objects):
                    return False
            elif teleport_pair.teleport2.rect.collidepoint(x, y):
                if not teleport_pair.teleport2.is_location_free(dx, dy, objects):
                    return False
        return True
    
    def _handle_block_collisions(self, new_x, new_y, dx, dy, grid_size, block_size, key, door, blocks, teleports):
        for block in blocks:
            if block.rect.collidepoint(new_x, new_y):
                if block.can_move:
                    block_new_x = block.rect.x + dx
                    block_new_y = block.rect.y + dy
                    if self._is_within_bounds(block_new_x, block_new_y, grid_size, block_size, door) and \
                       not self._collides_with_any(block_new_x, block_new_y, key, door, blocks, exclude=block):
                        block.move(dx, dy)
                        self._check_teleport_collision(teleports, dx, dy, blocks + [key, door], grid_size, block_size, obj=block)
                    else:
                        return True
                else:
                    return True
        return False

    def _handle_key_movement(self, dx, dy, block_size, grid_size, key, door, blocks, teleports):
        if key:
            key_new_x = key.rect.x + dx
            key_new_y = key.rect.y + dy
            if self.rect.colliderect(key.rect.move(-dx, -dy)):
                if self._is_within_bounds(key_new_x, key_new_y, grid_size, block_size, door) and \
                   not self._collides_with_any(key_new_x, key_new_y, None, None, blocks):
                    key.move(dx, dy)
                    self._check_teleport_collision(teleports, dx, dy, blocks, grid_size, block_size, obj=key)
                elif door and key_new_x == door.rect.x and key_new_y == door.rect.y:
                    key.move(dx, dy)
                    self._check_teleport_collision(teleports, dx, dy, blocks, grid_size, block_size, obj=key)
                else:
                    return True
        return False

    def _handle_door_movement(self, dx, dy, block_size, grid_size, door, blocks, teleports):
        if door and not door.open:
            door_new_x = door.rect.x + dx
            door_new_y = door.rect.y + dy
            if self.rect.colliderect(door.rect.move(-dx, -dy)):
                if self._is_within_bounds(door_new_x, door_new_y, grid_size, block_size, door) and \
                   not self._collides_with_any(door_new_x, door_new_y, None, None, blocks):
                    door.move(dx, dy)
                    self._check_teleport_collision(teleports, dx, dy, blocks, grid_size, block_size, obj=door)
                else:
                    return True
        return False

    def _collides_with_any(self, x, y, key, door, blocks, exclude=None):
        if key and key.rect.collidepoint(x, y):
            return True
        if door and door.rect.collidepoint(x, y):
            return True
        for block in blocks:
            if block != exclude and block.rect.collidepoint(x, y):
                return True
        return False
    
    def _check_teleport_collision(self, teleports, dx, dy, objects, grid_size, block_size, obj=None):
        for teleport_pair in teleports:
            if obj:
                teleport_pair.check_and_teleport(obj, dx, dy, objects, grid_size, block_size)
            else:
                teleport_pair.check_and_teleport(self, dx, dy, objects, grid_size, block_size)

    def record_movement(self, direction):
        self.movements.append(direction)

    def get_movements(self):
        return self.movements
    
    def undo_movement(self):
        if self.movements:
            dx, dy = self.movements.pop()
            self.rect.x -= dx
            self.rect.y -= dy
            return -dx, -dy
        else:
            return 0, 0

    async def shake(self, screen):
        original_position = self.rect.topleft
        shake_distance = 5
        for _ in range(5):
            self.rect.x += shake_distance
            self.draw(screen)
            pygame.display.update()
            await asyncio.sleep(0.01)
            self.rect.x -= shake_distance
            self.draw(screen)
            pygame.display.update()
            await asyncio.sleep(0.01)
        self.rect.topleft = original_position
        self.draw(screen)
        pygame.display.update()