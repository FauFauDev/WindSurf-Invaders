import pygame
import math
import random
from config import LARGEUR, HAUTEUR, BossConstants

class WarningIndicator:
    def __init__(self, x, y, width, height, duration=BossConstants.WARNING_DURATION, images=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = BossConstants.WARNING_ALPHA
        self.image = images['effects']['warning'] if images and 'effects' in images else None
        
    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        
        if progress >= 1:
            return True  # Indicator finished
            
        # Pulsing effect
        self.alpha = int(BossConstants.WARNING_ALPHA * (1 + math.sin(progress * math.pi * 4)) / 2)
        return False
        
    def draw(self, surface):
        if self.image:
            # Scale image to fit the rect
            scaled_image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            # Set alpha
            scaled_image.set_alpha(self.alpha)
            surface.blit(scaled_image, self.rect)
        else:
            # Fallback to shape drawing if image not available
            warning_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, (255, 0, 0, self.alpha), warning_surface.get_rect())
            surface.blit(warning_surface, self.rect)

class DangerZone:
    def __init__(self, x, y, radius, duration=BossConstants.DANGER_ZONE_DURATION, images=None, target=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = BossConstants.WARNING_ALPHA
        self.image = images['effects']['danger'] if images and 'effects' in images else None
        self.target = target  # Store reference to target (player ship)
        
    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        
        if progress >= 1:
            return True  # Zone finished
            
        # Update position if following a target
        if self.target and hasattr(self.target, 'rect'):
            self.x = self.target.rect.centerx
            self.y = self.target.rect.centery
            
        # Pulsing effect
        self.alpha = int(BossConstants.WARNING_ALPHA * (1 + math.sin(progress * math.pi * 6)) / 2)
        return False
        
    def draw(self, surface):
        if self.image:
            # Scale image to fit the danger zone
            size = self.radius * 2
            scaled_image = pygame.transform.scale(self.image, (size, size))
            # Set alpha
            scaled_image.set_alpha(self.alpha)
            surface.blit(scaled_image, (self.x - self.radius, self.y - self.radius))
        else:
            # Fallback to shape drawing if image not available
            warning_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(warning_surface, (255, 0, 0, self.alpha), (self.radius, self.radius), self.radius)
            surface.blit(warning_surface, (self.x - self.radius, self.y - self.radius))

class Particle:
    def __init__(self, x, y, color, velocity, lifetime=BossConstants.PARTICLE_LIFETIME, images=None, particle_type='particle'):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255
        self.image = images['effects'][particle_type] if images and 'effects' in images else None
        
    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.lifetime
        
        if progress >= 1:
            return True  # Particle finished
            
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.alpha = int(255 * (1 - progress))
        return False
        
    def draw(self, surface):
        if self.alpha > 0:
            if self.image:
                # Create a copy of the image for alpha modification
                particle_surface = self.image.copy()
                particle_surface.set_alpha(self.alpha)
                surface.blit(particle_surface, (int(self.x), int(self.y)))
            else:
                # Fallback to shape drawing if image not available
                color_with_alpha = (*self.color, self.alpha)
                particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color_with_alpha, (2, 2), 2)
                surface.blit(particle_surface, (int(self.x), int(self.y)))

class TransitionEffect:
    def __init__(self, duration=BossConstants.TRANSITION_DURATION, images=None):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.particles = []
        self.images = images
        self.generate_particles()
        
    def generate_particles(self, num_particles=50):
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = (random.randint(200, 255), random.randint(100, 200), 0)  # Orange-yellow colors
            self.particles.append(Particle(LARGEUR//2, HAUTEUR//2, color, velocity, images=self.images, particle_type='phase'))
            
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            return True  # Effect finished
            
        self.particles = [p for p in self.particles if not p.update()]
        return False
        
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class EffectManager:
    def __init__(self, images=None):
        self.warning_indicators = []
        self.danger_zones = []
        self.particles = []
        self.transition_effects = []
        self.images = images
        
    def add_warning(self, x, y, width, height, duration=BossConstants.WARNING_DURATION):
        self.warning_indicators.append(WarningIndicator(x, y, width, height, duration, self.images))
        
    def add_danger_zone(self, x, y, radius, duration=BossConstants.DANGER_ZONE_DURATION, target=None):
        self.danger_zones.append(DangerZone(x, y, radius, duration, self.images, target))
        
    def add_particles(self, x, y, num_particles=10, color=(255, 255, 0), particle_type='particle'):
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(x, y, color, velocity, images=self.images, particle_type=particle_type))
            
    def add_transition(self):
        self.transition_effects.append(TransitionEffect(images=self.images))
        
    def update(self):
        self.warning_indicators = [w for w in self.warning_indicators if not w.update()]
        self.danger_zones = [d for d in self.danger_zones if not d.update()]
        self.particles = [p for p in self.particles if not p.update()]
        self.transition_effects = [t for t in self.transition_effects if not t.update()]
        
    def draw(self, surface):
        for warning in self.warning_indicators:
            warning.draw(surface)
        for zone in self.danger_zones:
            zone.draw(surface)
        for particle in self.particles:
            particle.draw(surface)
        for transition in self.transition_effects:
            transition.draw(surface)
