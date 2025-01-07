import pygame
from game.player import Player
from game.door import Door
from game.key import Key

class Teleport:
    def __init__(self, x, y, width, height, target=None, image_path="assets/pixel_portal.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.target = target
        self.image_path = image_path
        self.load_image()

    def load_image(self):
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def teleport(self, obj, dx, dy, objects, grid_size, block_size):
        if self.target:
            new_x = self.target.rect.x + dx
            new_y = self.target.rect.y + dy
            target_obj = next((o for o in objects if o.rect.collidepoint(new_x, new_y)), None)
            if target_obj and isinstance(obj, Player) and target_obj.is_moveable():
                target_obj_new_x = target_obj.rect.x + dx
                target_obj_new_y = target_obj.rect.y + dy
                if isinstance(target_obj, Door) and target_obj.is_open():
                    obj.rect.x = new_x
                    obj.rect.y = new_y
                elif self._is_within_bounds(target_obj_new_x, target_obj_new_y, grid_size, block_size) and \
                   not any(o.rect.collidepoint(target_obj_new_x, target_obj_new_y) for o in objects):
                    target_obj.rect.x = target_obj_new_x
                    target_obj.rect.y = target_obj_new_y
                    target_obj.record_movement((dx, dy))
                    obj.rect.x = new_x
                    obj.rect.y = new_y
            elif not target_obj:
                if self._is_within_bounds(new_x, new_y, grid_size, block_size):
                    obj.rect.x = new_x
                    obj.rect.y = new_y

    def _is_within_bounds(self, x, y, grid_size, block_size):
        return block_size <= x < grid_size * block_size and block_size <= y < grid_size * block_size

    def is_location_free(self, dx, dy, objects):
        if self.target:
            new_x = self.target.rect.x + dx
            new_y = self.target.rect.y + dy
            return not any(o.rect.collidepoint(new_x, new_y) for o in objects)
        return False

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class TeleportPair:
    def __init__(self, x1, y1, x2, y2, width, height, image_path="assets/pixel_portal.png"):
        self.teleport1 = Teleport(x1, y1, width, height, image_path=image_path)
        self.teleport2 = Teleport(x2, y2, width, height, image_path=image_path)
        self.teleport1.target = self.teleport2
        self.teleport2.target = self.teleport1

    def draw(self, screen):
        self.teleport1.draw(screen)
        self.teleport2.draw(screen)

    def check_and_teleport(self, obj, dx, dy, objects, grid_size, block_size):
        if self.teleport1.rect.colliderect(obj.rect):
            self.teleport1.teleport(obj, dx, dy, objects, grid_size, block_size)
        elif self.teleport2.rect.colliderect(obj.rect):
            self.teleport2.teleport(obj, dx, dy, objects, grid_size, block_size)

    def move(self, dx, dy):
        self.teleport1.move(dx, dy)
        self.teleport2.move(dx, dy)

    def can_move_through_teleport(self, obj, new_pos, objects, grid_size, block_size):
        for teleport in [self.teleport1, self.teleport2]:
            if teleport.rect.collidepoint(new_pos):
                target_teleport = teleport.target
                target_new_x = target_teleport.rect.x + (new_pos[0] - teleport.rect.x)
                target_new_y = target_teleport.rect.y + (new_pos[1] - teleport.rect.y)
                if teleport._is_within_bounds(target_new_x, target_new_y, grid_size, block_size):
                    if isinstance(obj, Key) and any(isinstance(o, Door) and o.rect.collidepoint(target_new_x, target_new_y) for o in objects):
                        return True
                    if not any(o.rect.collidepoint(target_new_x, target_new_y) for o in objects):
                        return True
        return False