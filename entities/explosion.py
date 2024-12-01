import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, images, is_player=False):
        super().__init__()
        self.images = images
        self.delai_frame = 100 if is_player else 50
        self.image = self.images[0]  # Current image for sprite
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_index = 0
        self.derniere_update = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.derniere_update > self.delai_frame:
            self.frame_index += 1
            if self.frame_index < len(self.images):
                self.image = self.images[self.frame_index]
            self.derniere_update = current_time
        return self.frame_index >= len(self.images)

    def dessiner(self, fenetre):  # Keep the original French name for consistency
        if self.frame_index < len(self.images):
            fenetre.blit(self.image, self.rect)
            
    def draw(self, fenetre):  # Add alias for compatibility
        self.dessiner(fenetre)
