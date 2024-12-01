import pygame
import os
import random
from config import LARGEUR, HAUTEUR, ASSETS_DIR

class ParallaxBackground:
    def __init__(self):
        # Define background layers with their scroll speeds
        self.layer_configs = [
            # Front layer (fastest)
            {
                'pattern': 'Purple_Nebula_',
                'speed': 2.5,  # Increased from 2.0
                'options': ['01', '02', '03', '04', '05', '06', '07', '08']
            },
            # Middle layer
            {
                'pattern': 'Green_Nebula_',
                'speed': 0.8,  # Increased from 0.5
                'options': ['01', '02', '03', '04', '05', '06', '07', '08']
            },
            # Back layer (slowest)
            {
                'pattern': 'Blue_Nebula_',
                'speed': 0.3,  # Increased from 0.2
                'options': ['01', '02', '03', '04', '05', '06', '07', '08']
            }
        ]
        
        self.backgrounds = []
        self.layer_positions = []
        self.randomize_backgrounds()
        
    def randomize_backgrounds(self):
        """Randomize all background layers."""
        self.backgrounds = []
        self.layer_positions = []
        
        # Refresh random seed using current time
        random.seed()
        
        for config in self.layer_configs:
            # Randomly select a background from the options
            bg_num = random.choice(config['options'])
            bg_path = os.path.join(
                ASSETS_DIR,
                'backgrounds',
                f'{config["pattern"]}{bg_num}-1024x1024.png'
            )
            
            try:
                # Load and scale the image
                image = pygame.image.load(bg_path).convert_alpha()
                image = pygame.transform.scale(image, (LARGEUR, HAUTEUR))
                
                self.backgrounds.append({
                    'image': image,
                    'scroll_speed': config['speed']
                })
                self.layer_positions.append(0)
            except pygame.error as e:
                print(f"Error loading background {bg_path}: {e}")
                # Create a fallback solid color background
                fallback = pygame.Surface((LARGEUR, HAUTEUR))
                fallback.fill((0, 0, 30))  # Dark blue
                self.backgrounds.append({
                    'image': fallback,
                    'scroll_speed': config['speed']
                })
                self.layer_positions.append(0)
    
    def update(self):
        # Update each layer's position
        for i in range(len(self.backgrounds)):
            self.layer_positions[i] += self.backgrounds[i]['scroll_speed']
            # Reset position when the image has scrolled completely
            if self.layer_positions[i] >= HAUTEUR:
                self.layer_positions[i] = 0
    
    def draw(self, fenetre):
        # Draw each background layer
        for i, bg in enumerate(self.backgrounds):
            # Calculate positions for seamless scrolling
            pos_y = int(self.layer_positions[i])
            
            # Draw the main image
            fenetre.blit(bg['image'], (0, pos_y))
            
            # Draw the wrapped portion at the top
            if pos_y > 0:
                fenetre.blit(bg['image'], (0, pos_y - HAUTEUR))

    def fade_transition(self, fenetre, alpha=0):
        """Draw the background with a fade effect for level transitions."""
        # Create a surface for the fade effect
        fade_surface = pygame.Surface((LARGEUR, HAUTEUR))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        
        # Draw normal background first
        self.draw(fenetre)
        
        # Draw fade overlay
        fenetre.blit(fade_surface, (0, 0))
