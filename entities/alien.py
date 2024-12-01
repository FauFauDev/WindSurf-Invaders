"""
Space Invaders Alien Module

This module implements various types of aliens and their formation behaviors in the Space Invaders game.
It includes both standard aliens and formation-based aliens with unique movement patterns.

Classes:
    Envahisseur: Base alien class with standard movement and shooting mechanics
    FormationAlien: Advanced alien class that moves in specific patterns (triangle, circle, wave)

Formation Types:
    - Triangle: 5 rows increasing in size, front row shoots more frequently
    - Circle: Double circle formation (inner 8, outer 12 aliens) with orbital movement
    - Wave: 6 rows of 8 aliens moving in a wave pattern with synchronized shooting
"""

import pygame
import random
import math
from config import (
    VITESSE_ALIEN,
    HAUTEUR,
    FREQUENCE_TIR_ALIEN_BASE,
    FREQUENCE_TIR_REDUCTION_BOSS,
    VITESSE_ALIEN_POST_BOSS,
    LARGEUR
)

class Envahisseur:
    """
    Base alien class representing a single invader in the game.
    
    Attributes:
        image: Surface object containing the alien sprite
        rect: Rectangle for collision detection and positioning
        type_alien: Integer determining alien type (affects points and behavior)
        niveau: Current game level (affects speed and health)
        rangee: Row number in formation (affects points calculation)
        sante: Hit points, increases with game level
        points: Score value when destroyed
        chance_tir: Probability of shooting in any given frame
    """
    def __init__(self, x, y, type_alien, niveau, rangee, image, post_boss=False):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type_alien = type_alien
        self.niveau = niveau
        self.rangee = rangee
        self.vaisseau_index = rangee % 6
        self.direction = 1
        self.derniere_position = x
        self.dernier_tir = pygame.time.get_ticks()
        self.vitesse = (VITESSE_ALIEN + (niveau - 1) * 0.2) * (VITESSE_ALIEN_POST_BOSS if post_boss else 1)
        self.sante = 1 + (niveau // 3)
        self.y_initial = y
        self.limite_descente = HAUTEUR - 100
        
        # Points calculation
        self.points = 100 + (type_alien * 50) + ((5 - (rangee % 6)) * 25)
        self.points += (niveau - 1) * 25
        self.chance_tir = FREQUENCE_TIR_ALIEN_BASE * (1 + (niveau * 0.05))

    def deplacer(self):
        self.derniere_position = self.rect.x
        self.rect.x += self.direction * self.vitesse
        return self.rect.x

    def descendre(self, distance):
        self.rect.y += distance
        if self.rect.bottom > self.limite_descente:
            self.rect.bottom = self.limite_descente
            return True
        return False

    def tirer(self, boss_present=False):
        if boss_present:
            self.chance_tir *= FREQUENCE_TIR_REDUCTION_BOSS
        
        if random.random() < self.chance_tir:
            return True
        return False

    def prendre_degats(self, degats):
        self.sante -= degats
        return self.sante <= 0

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)

class FormationAlien(Envahisseur):
    """
    Advanced alien class that moves in specific formations.
    
    Inherits from Envahisseur and adds formation-specific movement and shooting patterns.
    
    Attributes:
        formation_id: String identifying formation type ('triangle', 'circle', 'wave')
        position_in_formation: Tuple containing position data:
            - Triangle: (row, column, total_columns)
            - Circle: (index, total_aliens, 'inner'/'outer')
            - Wave: (row, column, total_columns)
        
    Formation Behaviors:
        Triangle:
            - Increases in width with each row
            - Front row aliens shoot 50% more frequently
            
        Circle:
            - Two concentric circles with different radii
            - Outer circle aliens shoot 30% more frequently
            - Rotates around center point
            
        Wave:
            - Multiple rows moving in sine wave pattern
            - Shooting frequency increases at wave peaks/troughs
            - Phase calculated based on column position
    """
    def __init__(self, x, y, type_alien, niveau, rangee, image, formation_id, position_in_formation, post_boss=False):
        super().__init__(x, y, type_alien, niveau, rangee, image, post_boss)
        self.formation_id = formation_id
        self.position_in_formation = position_in_formation
        self.formation_offset_x = 0
        self.formation_offset_y = 0
        self.formation_angle = 0
        self.base_x = float(x)
        self.base_y = float(y)
        self.initial_x = float(x)  # Store the initial x position
        self.direction = 1
        self.global_offset_x = 0
        self.is_post_boss = post_boss  # Store post_boss state
        self.movement_speed = VITESSE_ALIEN * (1.5 if post_boss else 1.0)
        
        # Enhanced shooting attributes
        self.dernier_tir = pygame.time.get_ticks()
        # Increase shooting chance based on formation type and position
        if formation_id == 'triangle':
            # Front row aliens shoot more frequently
            self.chance_tir = FREQUENCE_TIR_ALIEN_BASE * (1.5 if position_in_formation[0] == 0 else 1.0)
        elif formation_id == 'circle':
            # Outer circle aliens shoot more frequently
            self.chance_tir = FREQUENCE_TIR_ALIEN_BASE * (1.3 if position_in_formation[2] == 'outer' else 1.0)
        else:  # wave formation
            # Front row aliens shoot more frequently
            self.chance_tir = FREQUENCE_TIR_ALIEN_BASE * (1.4 if position_in_formation[0] == 0 else 1.0)
        
        # Scale shooting chance with level
        self.chance_tir *= (1 + (niveau * 0.1))

    def update_formation_position(self, time, spacing=80):
        # Update global movement
        self.global_offset_x += self.movement_speed * self.direction
        
        # Different formation patterns based on formation_id
        if self.formation_id == 'triangle':
            # Triangle formation movement
            row = self.position_in_formation[0]
            col = self.position_in_formation[1]
            total_cols = self.position_in_formation[2]
            angle = time * 0.001  # Slower rotation
            
            # Calculate radius based on row (smaller radius to keep on screen)
            max_radius = min(LARGEUR, HAUTEUR) * 0.2  # Reduced to 20% of screen size
            radius = (max_radius / 5) * (row + 2)  # Scale radius by row
            
            # Calculate angle offset based on column position
            angle_offset = (2 * math.pi * col) / total_cols
            
            # Calculate position in rotating triangle
            self.formation_offset_x = math.cos(angle + angle_offset) * radius + self.global_offset_x
            self.formation_offset_y = math.sin(angle + angle_offset) * radius * 0.5  # Flattened vertically
            
        elif self.formation_id == 'circle':
            # Circle formation movement
            position = self.position_in_formation[0]
            total_positions = self.position_in_formation[1]
            circle_type = self.position_in_formation[2]
            
            # Different radius for inner and outer circle
            max_radius = min(LARGEUR, HAUTEUR) * 0.15  # Reduced to 15% of screen size
            radius = max_radius * (0.6 if circle_type == 'inner' else 1.0)
            
            # Calculate position in circle
            angle = (2 * math.pi * position / total_positions) + (time * 0.001)
            self.formation_offset_x = math.cos(angle) * radius + self.global_offset_x
            self.formation_offset_y = math.sin(angle) * radius
            
        else:  # wave formation
            # Wave formation movement
            row = self.position_in_formation[0]
            col = self.position_in_formation[1]
            total_cols = self.position_in_formation[2]
            
            # Adjusted spacing for tighter formation
            vertical_spacing = spacing * 0.6  # Reduced vertical spacing
            horizontal_spacing = spacing * 2.0  # Doubled horizontal spacing for clear separation
            
            # Calculate screen boundaries considering the formation width
            left_boundary = horizontal_spacing
            right_boundary = LARGEUR - (total_cols * horizontal_spacing)
            
            # Update global movement with reduced speed for better control
            self.movement_speed = VITESSE_ALIEN * (1.0 if self.is_post_boss else 0.8)  # Use stored post_boss state
            self.global_offset_x += self.movement_speed * self.direction
            
            # Check boundaries and update direction
            if self.global_offset_x > right_boundary - self.initial_x:
                self.direction = -1
                self.global_offset_x = right_boundary - self.initial_x
            elif self.global_offset_x < left_boundary - self.initial_x:
                self.direction = 1
                self.global_offset_x = left_boundary - self.initial_x
            
            # Calculate exact grid position with adjusted spacing
            grid_x = self.initial_x + (col * horizontal_spacing) + self.global_offset_x
            grid_y = self.base_y + (row * vertical_spacing)
            
            # Simple wave motion (only small vertical displacement)
            wave_amplitude = 8  # Further reduced amplitude
            wave_frequency = 0.001  # Keep same slow wave
            wave_offset = math.sin(time * wave_frequency) * wave_amplitude
            
            # Set final position maintaining grid structure
            self.rect.x = int(grid_x)
            self.rect.y = int(grid_y + wave_offset)
            return
            
        # Update position for other formations
        self.rect.x = int(self.base_x + self.formation_offset_x)
        self.rect.y = int(self.base_y + self.formation_offset_y)

    def tirer(self, boss_present=False):
        current_time = pygame.time.get_ticks()
        
        # Add cooldown between shots
        if current_time - self.dernier_tir < 1000:  # 1 second cooldown
            return False
            
        if boss_present:
            self.chance_tir *= FREQUENCE_TIR_REDUCTION_BOSS
        
        # Increase shooting chance based on position and pattern
        base_chance = self.chance_tir
        if self.formation_id == 'wave':
            # Increase chance when alien is at wave peak or trough
            # Use position[1] (col) / position[2] (total cols) for wave phase
            phase = (self.position_in_formation[1] / self.position_in_formation[2]) if self.position_in_formation[2] > 0 else 0
            wave_pos = math.sin(current_time * 0.002 + phase * 2 * math.pi)
            if abs(wave_pos) > 0.8:  # Near peak or trough
                base_chance *= 1.5
                
        elif self.formation_id == 'circle':
            # Increase chance when alien is at the bottom of the circle
            angle = current_time * 0.001 + (2 * math.pi * self.position_in_formation[0]) / self.position_in_formation[1]
            if math.sin(angle) > 0.7:  # When alien is lower in the circle
                base_chance *= 1.3
                
        # Random chance to fire
        if random.random() < base_chance:
            self.dernier_tir = current_time
            return True
            
        return False

def creer_envahisseurs(niveau, images, post_boss=False):
    """
    Factory function to create aliens in various formations.
    
    Args:
        niveau: Current game level
        images: List of alien sprite images
        post_boss: Boolean indicating if aliens appear after boss fight
        
    Returns:
        List of Envahisseur or FormationAlien objects
        
    Formation Selection:
        - Randomly chooses between triangle, circle, and wave formations
        - Falls back to classic formation if insufficient aliens created
        - Adjusts spacing and positioning based on screen dimensions
    """
    envahisseurs = []
    formation_types = ['triangle', 'circle', 'wave']
    # Increase chance of triangle formation
    weights = [0.4, 0.3, 0.3]  # 40% triangle, 30% circle, 30% wave
    current_formation = random.choices(formation_types, weights=weights)[0]
    spacing = 60  # Slightly reduced spacing for better visibility
    
    if current_formation == 'triangle':
        # Create triangle formation (5 rows increasing in size)
        rows = 5
        start_y = 150  # Start lower for better visibility
        for row in range(rows):
            # Each row has 2 more aliens than the previous one
            cols = row + 3
            for col in range(cols):
                x = LARGEUR // 2 - (cols * spacing // 2) + col * spacing
                y = start_y + row * spacing  # Start from the adjusted height
                type_alien = random.randint(0, 2)
                alien = FormationAlien(x, y, type_alien, niveau, row, 
                                     images[row % 6], 'triangle', 
                                     (row, col, cols), post_boss)
                envahisseurs.append(alien)
                
    elif current_formation == 'circle':
        # Create double circle formation (inner 8, outer 12 aliens)
        inner_aliens = 8
        outer_aliens = 12
        center_y = 200  # Lowered center point for better visibility
        
        # Inner circle
        for i in range(inner_aliens):
            x = LARGEUR // 2
            y = center_y  # Use the new center point
            type_alien = random.randint(0, 2)
            alien = FormationAlien(x, y, type_alien, niveau, 0, 
                                 images[i % 6], 'circle', 
                                 (i, inner_aliens, 'inner'), post_boss)
            envahisseurs.append(alien)
            
        # Outer circle
        for i in range(outer_aliens):
            x = LARGEUR // 2
            y = center_y  # Same center point as inner circle
            type_alien = random.randint(0, 2)
            alien = FormationAlien(x, y, type_alien, niveau, 1, 
                                 images[i % 6], 'circle', 
                                 (i, outer_aliens, 'outer'), post_boss)
            envahisseurs.append(alien)
            
    else:  # wave formation
        # Create wave formation with multiple rows and columns
        rows = 6  # Increased to 6 rows for more waves
        cols = 8  # 8 columns for good coverage
        start_y = 100  # Start higher to accommodate more rows
        for row in range(rows):
            for col in range(cols):
                # Calculate initial positions
                x = LARGEUR // 2 - (cols * spacing // 2) + col * spacing
                y = start_y + row * spacing
                type_alien = random.randint(0, 2)
                alien = FormationAlien(x, y, type_alien, niveau, row, 
                                     images[col % 6], 'wave', 
                                     (row, col, cols), post_boss)
                envahisseurs.append(alien)

    # If no formation was chosen or too few aliens, create classic formation
    if len(envahisseurs) < 15:
        envahisseurs = []
        rangees = 5
        colonnes = 11
        espace_x = spacing
        espace_y = spacing
        debut_x = (LARGEUR - (colonnes - 1) * espace_x) // 2  # Center horizontally
        debut_y = 80  # Start higher up
        
        for rangee in range(rangees):
            for colonne in range(colonnes):
                x = debut_x + colonne * espace_x
                y = debut_y + rangee * espace_y
                type_alien = rangee // 2
                alien = Envahisseur(x, y, type_alien, niveau, rangee, 
                                  images[rangee % 6], post_boss)
                envahisseurs.append(alien)
    
    return envahisseurs
