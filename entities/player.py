import pygame
from config import LARGEUR, HAUTEUR, DELAI_ENTRE_TIRS_JOUEUR, DELAI_ENTRE_TIRS_JOUEUR_RAPIDE
from effects.powerup_effects import PowerupEffectManager
import os
import random
import math

class PrecisionTracker:
    def __init__(self):
        self.tirs_total = 0
        self.tirs_reussis = 0
        self.current_streak = 0
        self.best_streak = 0
        self.font = pygame.font.Font(None, 24)
        self.last_milestone = 0
        self.milestone_flash = 0
        self.milestone_alpha = 0
        self.milestone_levels = [50, 70, 85, 95]
        self.milestone_colors = {
            50: (0, 255, 0),    # Green
            70: (0, 255, 255),  # Cyan
            85: (255, 255, 0),  # Yellow
            95: (255, 0, 255)   # Magenta
        }
    
    def obtenir_precision(self):
        if self.tirs_total == 0:
            return 0
        return (self.tirs_reussis / self.tirs_total) * 100
    
    def ajouter_tir(self, touche=False):
        self.tirs_total += 1
        if touche:
            self.tirs_reussis += 1
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
        else:
            self.current_streak = 0

class Joueur(pygame.sprite.Sprite):
    def __init__(self, sound_manager=None, player_img=None):
        super().__init__()
        # Use provided image or load default
        if player_img is not None:
            self.image = player_img
        else:
            # Load and scale the default player image
            original_image = pygame.image.load(os.path.join('assets', 'images', 'player', 'player1.png'))
            self.image = pygame.transform.scale(original_image, (80, 80))  # Scale to match menu size
        
        self.original_image = self.image.copy()  # Store original image for hit effect
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGEUR // 2
        self.rect.bottom = HAUTEUR - 20
        self.vitesse = 5  
        self.sound_manager = sound_manager
        
        # Hit effect
        self.hit_flash = False
        self.hit_flash_start = 0
        self.hit_flash_duration = 100  # Flash duration in milliseconds
        self.hit_particles = []
        
        # Collision box adjustment
        self.hitbox = self.rect.inflate(-20, -20)  # Smaller collision box
        
        # Energy system
        self.energie = 100
        self.derniere_recharge = pygame.time.get_ticks()
        
        # Shield
        self.shield_actif = False
        self.shield_temps = 0
        self.shield_duree = 5000  # 5 seconds
        
        # Rapid Fire
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.rapid_fire_duration = 5000  # 5 seconds
        self.fire_rate = DELAI_ENTRE_TIRS_JOUEUR  
        self.rapid_fire_rate = DELAI_ENTRE_TIRS_JOUEUR_RAPIDE  
        self.last_shot = 0
        
        # Effect Manager
        self.effect_manager = PowerupEffectManager()
        
        # Invincibility
        self.est_invincible = False
        self.temps_invincible = 0
        self.duree_invincibilite = 2000  # 2 seconds
        
        # Dash attributes
        self.dash_disponible = True
        self.dash_timer = 0
        self.dash_cooldown = 1500
        self.dash_vitesse = 12
        self.en_dash = False
        self.dash_direction = 0
        
        # Stats
        self.precision_tracker = PrecisionTracker()
        self.tirs_total = 0
        self.tirs_reussis = 0
        self.combo_kills = 0
        self.dernier_kill = 0
        self.multiplicateur_score = 1.0

    def set_sound_manager(self, sound_manager):
        self.sound_manager = sound_manager

    def deplacer(self):
        keys = pygame.key.get_pressed()
        self.derniere_position = self.rect.x
        
        if self.en_dash:
            self.rect.x += self.dash_direction * self.dash_vitesse
        else:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.vitesse
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.vitesse
        
        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGEUR:
            self.rect.right = LARGEUR

    def activer_dash(self, direction):
        if self.dash_disponible:
            self.en_dash = True
            self.dash_direction = direction
            self.dash_disponible = False
            self.dash_timer = pygame.time.get_ticks()

    def peut_tirer(self):
        current_time = pygame.time.get_ticks()
        delai = self.rapid_fire_rate if self.rapid_fire else self.fire_rate
        if current_time - self.last_shot > delai:
            self.last_shot = current_time
            return True
        return False

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update hitbox position with player
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery
        
        # Update hit flash effect
        if self.hit_flash and current_time - self.hit_flash_start > self.hit_flash_duration:
            self.hit_flash = False
            self.image = self.original_image.copy()
        
        # Update hit particles
        for particle in self.hit_particles[:]:
            particle['life'] -= 1
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            if particle['life'] <= 0:
                self.hit_particles.remove(particle)
        
        # Update shield status
        if self.shield_actif and current_time - self.shield_temps > self.shield_duree:
            self.shield_actif = False
            if self.effect_manager:
                self.effect_manager.active_shield = False
        
        # Update rapid fire status
        if self.rapid_fire and current_time - self.rapid_fire_timer > self.rapid_fire_duration:
            self.rapid_fire = False
            if self.effect_manager:
                self.effect_manager.active_rapid_fire = False
        
        # Update invincibility
        if self.est_invincible and current_time - self.temps_invincible > self.duree_invincibilite:
            self.est_invincible = False
        
        # Update dash cooldown
        if not self.dash_disponible and current_time - self.dash_timer > self.dash_cooldown:
            self.dash_disponible = True
        
        # Update effect manager
        if self.effect_manager:
            self.effect_manager.update(self.rect)
        
        # Rest of the update code...
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.vitesse
        if keys[pygame.K_RIGHT] and self.rect.right < LARGEUR:
            self.rect.x += self.vitesse
            
        # Recharge d'énergie
        if current_time - self.derniere_recharge >= 100:  # Recharge every 100ms
            if self.energie < 100:
                self.energie = min(100, self.energie + 1)
            self.derniere_recharge = current_time
            
        # Mise à jour du bouclier
        if self.shield_actif:
            if current_time - self.shield_temps > self.shield_duree:
                self.shield_actif = False
                if self.effect_manager:
                    self.effect_manager.active_shield = False
                
        # Mise à jour du tir rapide
        if self.rapid_fire:
            if current_time - self.rapid_fire_timer > self.rapid_fire_duration:
                self.rapid_fire = False
                if self.effect_manager:
                    self.effect_manager.active_rapid_fire = False
                
        # Mise à jour de l'invincibilité
        if self.est_invincible:
            if current_time - self.temps_invincible > self.duree_invincibilite:
                self.est_invincible = False
                
        # Mise à jour des effets
        if self.effect_manager:
            self.effect_manager.update(self.rect)

    def shoot(self):
        current_time = pygame.time.get_ticks()
        delai = self.rapid_fire_rate if self.rapid_fire else self.fire_rate
        if current_time - self.last_shot > delai:
            self.last_shot = current_time
            if self.sound_manager:
                self.sound_manager.play('shoot', 0.2)
            return True
        return False
            
    def activer_powerup(self, powerup_type):
        if powerup_type == "shield":
            self.shield_actif = True
            self.shield_temps = pygame.time.get_ticks()
            if self.sound_manager:
                self.sound_manager.play('shield', 0.7)
            if self.effect_manager:
                self.effect_manager.active_shield = True
                self.effect_manager.add_pickup_effect(
                    self.rect.centerx,
                    self.rect.centery,
                    powerup_type
                )
        elif powerup_type == "fire":
            self.rapid_fire = True
            self.rapid_fire_timer = pygame.time.get_ticks()
            if self.effect_manager:
                self.effect_manager.active_rapid_fire = True
                self.effect_manager.add_pickup_effect(
                    self.rect.centerx,
                    self.rect.centery,
                    powerup_type
                )
        elif powerup_type == "life":
            if self.sound_manager:
                self.sound_manager.play('health', 0.7)
            if self.effect_manager:
                self.effect_manager.add_pickup_effect(
                    self.rect.centerx,
                    self.rect.centery,
                    powerup_type
                )

    def prendre_degats(self):
        if not self.shield_actif and not self.est_invincible:
            current_time = pygame.time.get_ticks()
            
            # Activate hit flash
            self.hit_flash = True
            self.hit_flash_start = current_time
            
            # Create white flash effect
            flash_image = self.original_image.copy()
            flash_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = flash_image
            
            # Create particle effects
            num_particles = 20
            for _ in range(num_particles):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 5)
                self.hit_particles.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'life': random.randint(10, 20),
                    'color': (255, 100, 100)
                })
            
            # Play hit sound
            if self.sound_manager:
                self.sound_manager.play('hit', 0.3)
            
            self.est_invincible = True
            self.temps_invincible = current_time
            return True
        return False

    def dessiner(self, fenetre):
        # Draw hit particles
        for particle in self.hit_particles:
            pygame.draw.circle(fenetre, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             2)
        
        # Draw the player with flashing effect during invincibility
        if self.est_invincible and not self.shield_actif:
            if pygame.time.get_ticks() % 200 < 100:  # Blink every 100ms
                fenetre.blit(self.image, self.rect)
        else:
            fenetre.blit(self.image, self.rect)
        
        # Draw powerup effects
        if self.effect_manager:
            self.effect_manager.draw(fenetre)
        
        # Debug: Draw hitbox (comment out in production)
        # pygame.draw.rect(fenetre, (255, 0, 0), self.hitbox, 1)
