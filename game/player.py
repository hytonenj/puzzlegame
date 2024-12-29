import pygame

class Player:
    def __init__(self, x, y, width, height, image_path="assets/player.png"):
        self.movements = []
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def move(self, dx, dy, grid_size, block_size, key=None, door=None, blocks=[]):
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Check boundaries against the grid
        if (block_size <= new_x < (grid_size) * block_size and block_size <= new_y < (grid_size) * block_size) or (door and door.open == True and door.rect.collidepoint(new_x, new_y)):
            # Check for collisions with blocks
            if any(block.rect.collidepoint(new_x, new_y) for block in blocks):
                return  # Prevent player from moving if there's a collision with a block

            if key:
                key_new_x = key.rect.x + dx
                key_new_y = key.rect.y + dy

                # Check if the player is adjacent to the key and moving towards it
                if self.rect.colliderect(key.rect.move(-dx, -dy)):
                    # Check boundaries for the key or if it can move to the door's position
                    if (block_size <= key_new_x < (grid_size) * block_size and block_size <= key_new_y < (grid_size) * block_size) or (door and key.rect.collidepoint(door.rect.x, door.rect.y)):
                        # Check for collisions with blocks for the key
                        if any(block.rect.collidepoint(key_new_x, key_new_y) for block in blocks):
                            return  # Prevent key from moving if there's a collision with a block
                        key.move(dx, dy)
                    elif door and (key_new_x == door.rect.x and key_new_y == door.rect.y):
                        key.move(dx, dy)
                    else:
                        return  # Prevent player from moving if the key can't move

            self.rect.x = new_x
            self.rect.y = new_y
            self.record_movement((dx, dy))

    def record_movement(self, direction):
        self.movements.append(direction)

    def get_movements(self):
        return self.movements
    
    def undo_movement(self):
        if self.movements:
            dx, dy = self.movements.pop()
            self.rect.x -= dx
            self.rect.y -= dy

    def shake(self, screen):
        original_position = self.rect.topleft
        shake_distance = 5
        for _ in range(5):
            self.rect.x += shake_distance
            self.draw(screen)
            pygame.display.update()
            pygame.time.wait(10)
            self.rect.x -= shake_distance
            self.draw(screen)
            pygame.display.update()
            pygame.time.wait(10)
        self.rect.topleft = original_position
        self.draw(screen)
        pygame.display.update()