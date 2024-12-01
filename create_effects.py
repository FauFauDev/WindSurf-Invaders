import pygame
import os
import math

# Initialize Pygame
pygame.init()

# Create effects directory if it doesn't exist
effects_dir = os.path.join("assets", "images", "effects")
if not os.path.exists(effects_dir):
    os.makedirs(effects_dir)

# Create warning.png (64x64)
warning_size = 64
warning_surface = pygame.Surface((warning_size, warning_size), pygame.SRCALPHA)
warning_color = (255, 0, 0, 128)  # Semi-transparent red

# Draw warning triangle
points = [
    (warning_size//2, 5),
    (warning_size-5, warning_size-5),
    (5, warning_size-5)
]
pygame.draw.polygon(warning_surface, warning_color, points)
pygame.draw.polygon(warning_surface, (255, 0, 0), points, 2)  # Border

# Add exclamation mark
pygame.draw.rect(warning_surface, (255, 0, 0), (warning_size//2-2, warning_size//2-10, 4, 15))
pygame.draw.circle(warning_surface, (255, 0, 0), (warning_size//2, warning_size//2+10), 2)

pygame.image.save(warning_surface, os.path.join(effects_dir, "warning.png"))

# Create danger_zone.png (128x128)
zone_size = 128
zone_surface = pygame.Surface((zone_size, zone_size), pygame.SRCALPHA)
zone_color = (255, 0, 0, 64)  # Very transparent red

# Draw concentric circles
for radius in range(zone_size//2, 0, -10):
    alpha = int(128 * (radius/(zone_size//2)))
    color = (255, 0, 0, alpha)
    pygame.draw.circle(zone_surface, color, (zone_size//2, zone_size//2), radius, 2)

pygame.image.save(zone_surface, os.path.join(effects_dir, "danger_zone.png"))

# Create particle.png (4x4)
particle_size = 4
particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
pygame.draw.circle(particle_surface, (255, 255, 255, 255), (particle_size//2, particle_size//2), particle_size//2)
pygame.image.save(particle_surface, os.path.join(effects_dir, "particle.png"))

# Create damage_particle.png (4x4)
damage_particle = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
pygame.draw.circle(damage_particle, (255, 165, 0, 255), (particle_size//2, particle_size//2), particle_size//2)
pygame.image.save(damage_particle, os.path.join(effects_dir, "damage_particle.png"))

# Create teleport_particle.png (4x4)
teleport_particle = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
pygame.draw.circle(teleport_particle, (0, 255, 255, 255), (particle_size//2, particle_size//2), particle_size//2)
pygame.image.save(teleport_particle, os.path.join(effects_dir, "teleport_particle.png"))

# Create phase_transition.png (128x128)
transition_size = 128
transition_surface = pygame.Surface((transition_size, transition_size), pygame.SRCALPHA)

# Create a burst effect
center = transition_size // 2
for i in range(0, 360, 15):  # Create 24 rays
    angle = math.radians(i)
    end_x = center + math.cos(angle) * (transition_size//2)
    end_y = center + math.sin(angle) * (transition_size//2)
    
    # Draw each ray with gradient alpha
    for t in range(20):  # 20 segments per ray
        t = t / 20
        x = center + math.cos(angle) * (transition_size//2) * t
        y = center + math.sin(angle) * (transition_size//2) * t
        alpha = int(255 * (1 - t))
        pygame.draw.circle(transition_surface, (255, 255, 200, alpha), (int(x), int(y)), 2)

pygame.image.save(transition_surface, os.path.join(effects_dir, "phase_transition.png"))

print("Created effect images in", effects_dir)
pygame.quit()
