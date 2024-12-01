import math
import random
from config import LARGEUR, HAUTEUR, BossConstants
import pygame

class BossPattern:
    def __init__(self, boss):
        self.boss = boss
        self.start_time = 0
        self.duration = 2500  # Further reduced from 3000ms to 2500ms
        self.is_finished = False
        # Cache screen boundaries and center positions
        self.center_x = (boss.min_x + boss.max_x) / 2
        self.center_y = (boss.min_y + boss.max_y) / 2
        self.width = (boss.max_x - boss.min_x)
        self.height = (boss.max_y - boss.min_y)
        
    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.is_finished = False
        
    def update(self, player_pos):
        """Returns True if pattern is finished"""
        if self.is_finished:
            return True
            
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        
        if progress >= 1:
            self.is_finished = True
            return True
            
        return False
        
    def get_position(self):
        return self.boss.rect.centerx, self.boss.rect.centery
        
    def get_player_position(self, player_pos):
        """Helper method to get player coordinates regardless of input type"""
        if player_pos is None:
            return None, None
            
        if hasattr(player_pos, 'rect'):
            return player_pos.rect.centerx, player_pos.rect.centery
        return player_pos[0], player_pos[1]

class SineWavePattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.amplitude = boss.amplitude_y * 1.2  # Increased amplitude
        # Pre-calculate movement values
        self.base_speed = boss.speed * 1.5
        
    def start(self):
        super().start()
        self.boss.velocity = [self.base_speed * self.boss.direction, 0]
        
    def update(self, player_pos):
        if super().update(player_pos):  # Check if pattern should end
            return True
            
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
            
        # Check screen bounds and reverse direction if needed
        if (self.boss.rect.centerx >= self.boss.max_x - 10 and self.boss.velocity[0] > 0) or \
           (self.boss.rect.centerx <= self.boss.min_x + 10 and self.boss.velocity[0] < 0):
            self.boss.direction *= -1
            self.boss.velocity[0] = self.base_speed * self.boss.direction
            
        # Update vertical movement (sine wave) with smoother transitions
        wave = math.sin(progress * math.pi * 4)  # Reduced frequency for smoother movement
        target_y = self.center_y + wave * self.amplitude
        self.boss.velocity[1] = (target_y - self.boss.rect.centery) * 0.1  # Smoother vertical movement
        return False

class Figure8Pattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        # Pre-calculate pattern dimensions
        self.pattern_width = self.width * 0.35  # Slightly reduced width
        self.pattern_height = self.height * 0.6  # Slightly reduced height
        self.smoothing = 0.1  # Movement smoothing factor
        
    def start(self):
        super().start()
        self.boss.velocity = [0, 0]
        
    def update(self, player_pos):
        progress = (self.boss.current_time - self.start_time) / self.duration
        if progress >= 1:
            return True
            
        t = progress * math.pi * 2  # Reduced speed for smoother movement
        
        # Calculate new position with smoother movement using cached values
        new_x = self.center_x + math.sin(t * 2) * self.pattern_width
        new_y = self.center_y + math.sin(t) * self.pattern_height
        
        # Smoother velocity updates
        dx = new_x - self.boss.rect.centerx
        dy = new_y - self.boss.rect.centery
        self.boss.velocity[0] = dx * self.smoothing
        self.boss.velocity[1] = dy * self.smoothing
        return False

class SpiralPattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.duration = 4000  # Slightly longer for spiral
        # Pre-calculate pattern values
        self.radius_start = min(self.width, self.height) * 0.25
        self.radius_end = min(self.width, self.height) * 0.4
        self.smoothing = 0.15
        
    def start(self):
        super().start()
        self.boss.velocity = [0, 0]
        
    def update(self, player_pos):
        progress = (self.boss.current_time - self.start_time) / self.duration
        if progress >= 1:
            return True
            
        # Calculate spiral movement with optimized calculations
        angle = progress * math.pi * 8  # 4 full rotations
        radius = self.radius_start + (self.radius_end - self.radius_start) * progress
        
        new_x = self.center_x + math.cos(angle) * radius
        new_y = self.center_y + math.sin(angle) * radius
        
        # Update velocity with smoothing
        dx = new_x - self.boss.rect.centerx
        dy = new_y - self.boss.rect.centery
        self.boss.velocity[0] = dx * self.smoothing
        self.boss.velocity[1] = dy * self.smoothing
        return False

class PincerPattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.duration = 2500  # Shorter duration for more aggressive movement
        
    def start(self):
        super().start()
        self.phase = 0
        self.target_x = 0 if random.random() < 0.5 else LARGEUR
        self.boss.velocity = [0, 0]
        
    def update(self, player_pos):
        if player_pos is None:
            return True
            
        progress = (self.boss.current_time - self.start_time) / self.duration
        if progress >= 1:
            return True
            
        # Get player position coordinates
        player_x, player_y = self.get_player_position(player_pos)
        if player_x is None:  # No valid player position
            return True
            
        if self.phase == 0:  # Quick move to side
            dx = self.target_x - self.boss.rect.centerx
            if abs(dx) < self.boss.speed * 2:
                self.phase = 1
            else:
                self.boss.velocity[0] = math.copysign(self.boss.speed * 2, dx)
                
        else:  # Attack
            dx = player_x - self.boss.rect.centerx
            dy = player_y - self.boss.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.boss.velocity[0] = (dx / dist) * self.boss.speed * 3
                self.boss.velocity[1] = (dy / dist) * self.boss.speed * 1.5
                    
        return False

class TeleportPattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.teleports = 0
        self.max_teleports = 3
        self.last_teleport = 0
        
    def start(self):
        super().start()
        self.teleports = 0
        self.last_teleport = self.start_time
        self.boss.velocity = [0, 0]
        
    def update(self, player_pos):
        if self.teleports >= self.max_teleports:
            return True
            
        current_time = self.boss.current_time
        if current_time - self.last_teleport > 1000:  # Teleport every second
            # Add warning effect before teleport
            self.boss.effect_manager.add_warning(
                self.boss.rect.x, self.boss.rect.y,
                self.boss.rect.width, self.boss.rect.height,
                500  # Warning duration
            )
            
            # Teleport after warning
            if current_time - self.last_teleport > 1500:
                self.boss.rect.centerx = random.randint(100, LARGEUR - 100)
                self.boss.rect.centery = random.randint(self.boss.min_y, self.boss.max_y)
                self.teleports += 1
                self.last_teleport = current_time
                
                # Add particle effect at new position
                self.boss.effect_manager.add_particles(
                    self.boss.rect.centerx,
                    self.boss.rect.centery,
                    20,  # Number of particles
                    (0, 255, 255)  # Cyan color
                )
                
        return False

class BerserkPattern(BossPattern):
    def __init__(self, boss):
        super().__init__(boss)
        self.next_change = 0
        self.change_interval = 500  # Change direction every 0.5 seconds
        
    def update(self, player_pos):
        progress = (self.boss.current_time - self.start_time) / self.duration
        if progress >= 1:
            return True
            
        if self.boss.current_time >= self.next_change:
            # Random direction change
            angle = random.uniform(0, math.pi * 2)
            speed = self.boss.speed * BossConstants.BERSERK_SPEED_MULTIPLIER
            self.boss.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.next_change = self.boss.current_time + self.change_interval
            
            # Add particle trail
            self.boss.effect_manager.add_particles(
                self.boss.rect.centerx,
                self.boss.rect.centery,
                5,  # Fewer particles but continuous
                (255, 0, 0)  # Red color
            )
            
        # Apply velocity
        self.boss.rect.x += self.boss.velocity[0]
        self.boss.rect.y += self.boss.velocity[1]
        
        # Bounce off screen edges
        if self.boss.rect.left < 0 or self.boss.rect.right > LARGEUR:
            self.boss.velocity = (-self.boss.velocity[0], self.boss.velocity[1])
        if self.boss.rect.top < self.boss.min_y or self.boss.rect.bottom > self.boss.max_y:
            self.boss.velocity = (self.boss.velocity[0], -self.boss.velocity[1])
            
        return False
