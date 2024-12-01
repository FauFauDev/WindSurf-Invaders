import pygame
import math
import random

class PowerupEffect:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 30
        self.max_radius = 60
        self.growth_rate = 2
        self.alpha = 255
        self.fade_rate = 5
        self.particles = []
        self.spawn_particles()

    def spawn_particles(self):
        for _ in range(12):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'alpha': 255,
                'size': random.randint(2, 4)
            })

    def update(self):
        # Update main circle effect
        self.radius += self.growth_rate
        self.alpha -= self.fade_rate

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] -= 5
            if particle['alpha'] <= 0:
                self.particles.remove(particle)

        # Return True if the effect is finished
        return self.alpha <= 0 and not self.particles

    def draw(self, screen):
        # Draw main circle effect
        if self.alpha > 0:
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, self.alpha), 
                             (self.radius, self.radius), self.radius, 2)
            screen.blit(surface, (self.x - self.radius, self.y - self.radius))

        # Draw particles
        for particle in self.particles:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, particle['alpha']),
                             (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, 
                       (particle['x'] - particle['size'], 
                        particle['y'] - particle['size']))

class ShieldEffect(PowerupEffect):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 255))  # Cyan color for shield
        self.shield_radius = 40
        self.shield_alpha = 128
        self.shield_pulse = 0

    def update(self):
        result = super().update()
        self.shield_pulse = (self.shield_pulse + 0.1) % (math.pi * 2)
        return result

    def draw(self, screen):
        super().draw(screen)
        if self.alpha > 0:
            # Draw pulsing shield effect
            pulse_radius = self.shield_radius + math.sin(self.shield_pulse) * 5
            shield_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*self.color, self.shield_alpha),
                             (pulse_radius, pulse_radius), pulse_radius, 2)
            screen.blit(shield_surface,
                       (self.x - pulse_radius, self.y - pulse_radius))

class HealthEffect(PowerupEffect):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 0))  # Green color for health
        self.cross_size = 20
        self.cross_alpha = 255

    def update(self):
        result = super().update()
        self.cross_alpha = max(0, self.cross_alpha - 5)
        return result

    def draw(self, screen):
        super().draw(screen)
        if self.cross_alpha > 0:
            # Draw health cross
            surface = pygame.Surface((self.cross_size * 2, self.cross_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*self.color, self.cross_alpha),
                           (self.cross_size - 3, 0, 6, self.cross_size * 2))
            pygame.draw.rect(surface, (*self.color, self.cross_alpha),
                           (0, self.cross_size - 3, self.cross_size * 2, 6))
            screen.blit(surface,
                       (self.x - self.cross_size, self.y - self.cross_size))

class FireEffect(PowerupEffect):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 165, 0))  # Orange color for fire powerup
        self.flame_particles = []
        for _ in range(15):
            self.flame_particles.append({
                'x': self.x,
                'y': self.y,
                'speed': random.uniform(2, 4),
                'angle': random.uniform(-math.pi/4, math.pi/4),
                'size': random.randint(3, 6),
                'alpha': 255
            })

    def update(self):
        result = super().update()
        
        # Update flame particles
        for particle in self.flame_particles[:]:
            particle['y'] -= particle['speed']
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['alpha'] -= 10
            
            if particle['alpha'] <= 0:
                self.flame_particles.remove(particle)
            
        # Spawn new particles while effect is active
        if self.alpha > 0 and len(self.flame_particles) < 15:
            self.flame_particles.append({
                'x': self.x,
                'y': self.y,
                'speed': random.uniform(2, 4),
                'angle': random.uniform(-math.pi/4, math.pi/4),
                'size': random.randint(3, 6),
                'alpha': 255
            })
            
        return result and not self.flame_particles

    def draw(self, screen):
        super().draw(screen)
        
        # Draw flame particles
        for particle in self.flame_particles:
            surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, particle['alpha']),
                             (particle['size'], particle['size']), particle['size'])
            screen.blit(surface,
                       (particle['x'] - particle['size'],
                        particle['y'] - particle['size']))

class RapidFireEffect:
    def __init__(self, player_rect):
        self.rect = player_rect
        self.particles = []
        self.color = (255, 165, 0)  # Orange
        
    def update(self):
        # Add new particles
        if len(self.particles) < 20:
            x = self.rect.centerx + random.randint(-20, 20)
            y = self.rect.bottom + random.randint(0, 10)
            speed = random.uniform(2, 5)
            size = random.randint(2, 4)
            self.particles.append({
                'pos': [x, y],
                'speed': speed,
                'size': size,
                'alpha': 255
            })
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['pos'][1] += particle['speed']
            particle['alpha'] -= 10
            
            if particle['alpha'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, surface):
        for particle in self.particles:
            pos = particle['pos']
            size = particle['size']
            alpha = particle['alpha']
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (size, size), size)
            surface.blit(particle_surface, (pos[0] - size, pos[1] - size))

class PowerupEffectManager:
    def __init__(self):
        self.effects = []
        self.active_shield = False
        self.active_rapid_fire = False
        self.player_rect = None

    def add_pickup_effect(self, x, y, powerup_type):
        if powerup_type == "shield":
            self.effects.append(ShieldEffect(x, y))
            self.active_shield = True
        elif powerup_type == "life":
            self.effects.append(HealthEffect(x, y))
        elif powerup_type == "fire":
            self.effects.append(FireEffect(x, y))
            self.active_rapid_fire = True

    def update(self, player_rect=None):
        if player_rect:
            self.player_rect = player_rect
        
        # Update effects and remove only if they return True (indicating they're finished)
        for effect in self.effects[:]:
            if effect.update():
                self.effects.remove(effect)

    def draw(self, screen):
        for effect in self.effects:
            effect.draw(screen)
        
        # Draw active shield effect if shield is active
        if self.active_shield and self.player_rect:
            shield_surface = pygame.Surface((self.player_rect.width + 20, 
                                          self.player_rect.height + 20), 
                                         pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surface, (0, 255, 255, 80),
                              shield_surface.get_rect(), 2)
            screen.blit(shield_surface,
                       (self.player_rect.centerx - shield_surface.get_width()//2,
                        self.player_rect.centery - shield_surface.get_height()//2))
        
        # Draw rapid fire effect if active
        if self.active_rapid_fire and self.player_rect:
            for _ in range(2):
                x = self.player_rect.centerx + random.randint(-20, 20)
                y = self.player_rect.bottom + random.randint(0, 10)
                size = random.randint(2, 4)
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 165, 0, 200),
                                 (size, size), size)
                screen.blit(surface, (x - size, y - size))
