import pygame
import random
import math
import os
from config import LARGEUR, HAUTEUR

class MysteryAlien(pygame.sprite.Sprite):
    def __init__(self, sound_manager=None):
        super().__init__()
        # Load a random mystery alien image
        self.image_number = random.randint(1, 20)
        image_path = os.path.join('assets', 'images', 'misteryAliens', f'{self.image_number}.png')
        self.original_image = pygame.image.load(image_path).convert_alpha()
        # Scale the image to be visible but not too large and cache it
        self.base_image = pygame.transform.scale(self.original_image, (80, 80))
        self.image = self.base_image
        self.rect = self.image.get_rect()
        
        # Initialize position randomly at the top
        self.rect.x = random.randint(100, LARGEUR - 100)  # Keep away from edges
        self.rect.y = 50  # Start a bit below the top to be visible
        
        # Movement variables - optimize by pre-calculating some values
        self.speed = random.uniform(1, 2)  # Even slower speed
        self.angle = 0
        self.amplitude = random.randint(100, 200)
        self.frequency = random.uniform(0.01, 0.02)
        self.base_x = float(self.rect.x)
        self.current_y = float(self.rect.y)
        self.time_alive = 0
        self.movement_pattern = random.choice(['wave', 'zigzag', 'circular'])
        self.direction = 1  # For zigzag pattern
        self.sound_manager = sound_manager
        self.is_alive = True  # Renamed from alive to is_alive
        
        # Pre-calculate movement constants
        self.vertical_speed = self.speed * 0.5  # Pre-calculate for wave and zigzag
        self.circular_speed = self.speed * 0.3  # Pre-calculate for circular
        self.zigzag_speed = self.speed * 2  # Pre-calculate for zigzag
        self.rotation_step = 0.5  # Slower rotation
        
        # Cache screen boundaries
        self.min_x = 50
        self.max_x = LARGEUR - 50 - self.rect.width
        
        # Optimization: Only rotate every N frames
        self.rotation_frame_skip = 6  # Rotate every 6 frames
        self.cached_rotated_images = {}  # Cache for rotated images
        
        print(f"Mystery Alien spawned: Pattern={self.movement_pattern}, Position=({self.rect.x}, {self.rect.y})")
        
    def update(self):
        if not self.is_alive:  # Updated check
            return
            
        self.time_alive += 1
        
        if self.movement_pattern == 'wave':
            # Sinusoidal wave movement - optimized calculations
            self.current_y += self.vertical_speed
            self.rect.y = int(self.current_y)
            self.rect.x = int(self.base_x + math.sin(self.time_alive * self.frequency) * self.amplitude)
            
        elif self.movement_pattern == 'zigzag':
            # Zigzag movement - optimized with pre-calculated values
            self.current_y += self.vertical_speed
            self.rect.y = int(self.current_y)
            if abs(self.rect.x - self.base_x) > self.amplitude:
                self.direction *= -1
            self.rect.x += self.zigzag_speed * self.direction
            
        elif self.movement_pattern == 'circular':
            # Circular movement - optimized calculations
            self.current_y += self.circular_speed
            self.rect.y = int(self.current_y)
            self.rect.x = int(self.base_x + math.cos(self.time_alive * self.frequency) * self.amplitude)
        
        # Keep the alien within screen bounds using cached values
        self.rect.x = max(self.min_x, min(self.rect.x, self.max_x))
        
        # Optimize rotation by only updating every N frames and using cached rotated images
        if self.time_alive % self.rotation_frame_skip == 0:
            self.angle = (self.angle + self.rotation_step) % 360
            # Check if we have this angle cached
            if self.angle not in self.cached_rotated_images:
                rotated = pygame.transform.rotate(self.base_image, self.angle)
                self.cached_rotated_images[self.angle] = rotated
                # Limit cache size
                if len(self.cached_rotated_images) > 720:  # Keep at most 720 angles (every 0.5 degrees)
                    self.cached_rotated_images.pop(next(iter(self.cached_rotated_images)))
            
            self.image = self.cached_rotated_images[self.angle]
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # Print position every 60 frames (about once per second)
        if self.time_alive % 60 == 0:
            print(f"Mystery alien at position: ({self.rect.x}, {self.rect.y})")
        
        # Check if alien has reached the bottom
        if self.rect.top > HAUTEUR:
            print(f"Mystery Alien reached bottom: Position=({self.rect.x}, {self.rect.y})")
            self.is_alive = False  # Updated property name
            return True  # Indicate that alien reached bottom
        return False  # Alien hasn't reached bottom

    def hit(self):
        """Handle being hit by player projectile"""
        if self.sound_manager:
            self.sound_manager.play('explosion', 0.3)
        print(f"Mystery Alien hit at position ({self.rect.x}, {self.rect.y})")
        self.is_alive = False  # Updated property name
        return 150  # Points for hitting mystery alien
