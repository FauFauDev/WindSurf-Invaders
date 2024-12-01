import pygame
import random
import math
from .boss_patterns import *
from effects.visual_effects import EffectManager
from entities.explosion import Explosion
from config import LARGEUR, HAUTEUR, BossConstants

class Boss(pygame.sprite.Sprite):
    def __init__(self, niveau, image, images=None, sound_manager=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.sound_manager = sound_manager
        self.images = images  # Store the game images
        
        # Use the pre-scaled image directly
        try:
            self.original_image = image
            self.image = self.original_image.copy()
        except Exception as e:
            print(f"Error initializing boss image: {e}")
            raise
            
        self.rect = self.image.get_rect()
        
        # Position initiale - start at top center
        self.rect.centerx = LARGEUR // 2
        self.rect.top = 50  # Start higher up
        
        # Movement boundaries - adjusted for smoother movement
        padding = 40  # Increased padding
        self.min_x = padding  # Left boundary
        self.max_x = LARGEUR - padding  # Right boundary
        self.min_y = 50  # Top boundary
        self.max_y = HAUTEUR // 3  # Bottom boundary (top third of screen)
        
        # Stats based on level - pre-calculate values
        self.niveau = niveau
        self.base_health = BossConstants.HP_BASE
        self.max_health = self.base_health * (1 + (niveau - 1) * BossConstants.HP_NIVEAU_MULTIPLIER)
        self.health = self.max_health
        self.base_speed = BossConstants.VITESSE_BASE
        self.speed = min(self.base_speed * (1 + (niveau - 1) * 0.2), 8)  # Cap speed at 8
        self.points = BossConstants.POINTS * niveau
        
        # State and pattern optimization
        self.direction = 1
        self.phase = 1
        self.current_time = pygame.time.get_ticks()
        self.last_shot = self.current_time
        self.dernier_tir = self.current_time
        self.explosions = pygame.sprite.Group()
        self.damaged_timer = 0
        self.damaged_duration = 100
        self.is_dead = False
        self.en_rage = False
        self.temps_invulnerable = 0
        self.duree_invulnerabilite = BossConstants.VULNERABILITE_DUREE
        self.vulnerable = True
        
        # Visual feedback optimization
        self.flash_timer = 0
        self.flash_duration = 200
        self.flash_image = self.create_flash_image()
        
        # Pattern attributes - pre-calculate common values
        self.angle_rotation = 0
        self.amplitude_y = 50
        self.frequence_y = 0.05
        self.pattern_time = pygame.time.get_ticks()
        self.pattern_duration = 5000
        self.dash_speed = self.speed * 3
        self.dash_target = None
        self.dash_cooldown = 0
        self.dash_cooldown_duration = 3000
        
        # Pattern management optimization
        self.effect_manager = EffectManager(images)
        self.available_patterns = {
            1: [SineWavePattern],  # Start with simple patterns
            2: [SineWavePattern, Figure8Pattern],
            3: [Figure8Pattern, SpiralPattern, PincerPattern]
        }
        self.current_pattern = None
        self.pattern_cooldown = 0
        
        # Pre-calculate phase thresholds
        self.phase_thresholds = {
            2: self.max_health * 0.7,
            3: self.max_health * 0.3
        }
        
        # Movement optimization
        self.shot_cooldown = BossConstants.SHOT_COOLDOWN
        self.velocity = [0, 0]
        self.select_new_pattern()

    def update(self, player_pos=None):
        # Cache current time to avoid multiple calls
        self.current_time = pygame.time.get_ticks()
        
        # Early return for dead state
        if self.is_dead:
            self.explosions.update()
            self.effect_manager.update()
            return
        
        # Update invulnerability state
        if not self.vulnerable and self.current_time - self.temps_invulnerable > self.duree_invulnerabilite:
            self.vulnerable = True
        
        # Update flash state
        if self.flash_timer > 0 and self.current_time - self.flash_timer > self.flash_duration:
            self.flash_timer = 0
        
        # Pattern management
        if self.pattern_cooldown > 0:
            if self.current_time >= self.pattern_cooldown:
                self.pattern_cooldown = 0
                self.select_new_pattern()
        elif self.current_pattern:
            if self.current_pattern.update(player_pos):  # Pattern finished
                self.pattern_cooldown = self.current_time + 250  # Reduced cooldown
                self.current_pattern = None
        else:  # No pattern and no cooldown
            self.select_new_pattern()
        
        # Update position
        self.deplacer(player_pos)
        
        # Update effects
        self.effect_manager.update()
        self.explosions.update()

    def deplacer(self, position_joueur=None):
        # Apply velocity with smooth boundary checks
        new_x = self.rect.centerx + self.velocity[0]
        new_y = self.rect.centery + self.velocity[1]
        
        # Smooth boundary enforcement with increased bounce
        if new_x < self.min_x:
            new_x = self.min_x + 5  # Push slightly away from boundary
            self.velocity[0] = abs(self.velocity[0])  # Ensure positive velocity
        elif new_x > self.max_x:
            new_x = self.max_x - 5  # Push slightly away from boundary
            self.velocity[0] = -abs(self.velocity[0])  # Ensure negative velocity
            
        if new_y < self.min_y:
            new_y = self.min_y + 5  # Push slightly away from boundary
            self.velocity[1] = abs(self.velocity[1])  # Ensure positive velocity
        elif new_y > self.max_y:
            new_y = self.max_y - 5  # Push slightly away from boundary
            self.velocity[1] = -abs(self.velocity[1])  # Ensure negative velocity
        
        # Update position
        self.rect.centerx = new_x
        self.rect.centery = new_y
        
    def tirer(self, position_joueur):
        current_time = pygame.time.get_ticks()
        delai = BossConstants.DELAI_TIR * (0.7 if self.en_rage else 1.0)  # Faster shooting in rage mode
        
        if current_time - self.dernier_tir > delai:
            self.dernier_tir = current_time
            
            # Add warning before shooting
            if position_joueur:
                # For compatibility with both position tuples and player objects
                if hasattr(position_joueur, 'rect'):
                    target = position_joueur  # It's a player object
                    pos = (position_joueur.rect.centerx, position_joueur.rect.centery)
                else:
                    target = None
                    pos = position_joueur
                
                self.effect_manager.add_danger_zone(
                    pos[0], pos[1],
                    radius=30,
                    duration=500,
                    target=target  # Pass the player object as target
                )
            
            return self.creer_projectiles(position_joueur)
        return []

    def creer_projectiles(self, position_joueur):
        projectiles = []
        
        # Get player position coordinates
        if hasattr(position_joueur, 'rect'):
            # If we received a Player object
            player_x = position_joueur.rect.centerx
            player_y = position_joueur.rect.centery
        else:
            # If we received a position tuple
            player_x, player_y = position_joueur
        
        if self.phase == 1:
            # Phase 1: Spread shots
            angles = [-45, -30, 0, 30, 45] if self.en_rage else [-30, 0, 30]
            vitesse = 4 if self.en_rage else 3
            
            for angle in angles:
                rad_angle = math.radians(angle)
                dx = math.sin(rad_angle) * vitesse
                dy = math.cos(rad_angle) * vitesse
                projectiles.append((self.rect.centerx, self.rect.bottom, dx, dy))
        else:
            # Phase 2: Aimed shots plus spread
            dx = player_x - self.rect.centerx
            dy = player_y - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                vitesse = 5 if self.en_rage else 4
                dx = (dx / distance) * vitesse
                dy = (dy / distance) * vitesse
                
                # Add main shot
                projectiles.append((self.rect.centerx, self.rect.bottom, dx, dy))
                
                # Add side shots in rage mode
                if self.en_rage:
                    angles = [-15, 15]
                    for angle in angles:
                        rad_angle = math.radians(angle)
                        new_dx = dx * math.cos(rad_angle) - dy * math.sin(rad_angle)
                        new_dy = dx * math.sin(rad_angle) + dy * math.cos(rad_angle)
                        projectiles.append((self.rect.centerx, self.rect.bottom, new_dx, new_dy))
        
        return projectiles

    def prendre_degats(self, degats):
        if not self.vulnerable:
            return False
        
        # Store old health for transition checks
        old_health = self.health
        
        # Apply damage with resistance
        actual_damage = degats * BossConstants.DAMAGE_RESISTANCE
        
        # Calculate new health but don't apply it yet
        new_health = self.health - actual_damage
        
        # Check if this damage would trigger a phase transition
        entering_phase_3 = not self.en_rage and new_health <= self.phase_thresholds.get(3, 0)
        entering_phase_2 = self.phase == 1 and new_health <= self.phase_thresholds.get(2, 0)
        
        # If entering a new phase, ensure we don't drop below the threshold too quickly
        if entering_phase_3:
            new_health = max(new_health, self.phase_thresholds.get(3, 0) + 1)
        elif entering_phase_2:
            new_health = max(new_health, self.phase_thresholds.get(2, 0) + 1)
            
        # Apply the adjusted damage
        self.health = new_health
        
        # Update visual state
        self.flash_timer = self.current_time
        self.temps_invulnerable = self.current_time
        self.vulnerable = False
        
        # Add damage particles
        self.effect_manager.add_particles(
            self.rect.centerx, 
            self.rect.centery,
            num_particles=15,
            color=(255, 0, 0),
            particle_type='damage'
        )
        
        # Check for death only if not transitioning phases
        if not (entering_phase_2 or entering_phase_3):
            if self.health <= 0:
                self.die()
                return True
        
        # Handle phase transitions
        old_phase = self.phase
        if entering_phase_3:
            self.phase = 3
            self.en_rage = True
            print(f"Boss entering rage mode at {self.health}/{self.max_health} HP")
        elif entering_phase_2:
            self.phase = 2
            print(f"Boss entering phase 2 at {self.health}/{self.max_health} HP")
        
        # Add transition effects if phase changed
        if old_phase != self.phase:
            self.effect_manager.add_transition()
            self.effect_manager.add_warning(
                self.rect.x,
                self.rect.y,
                self.rect.width + 20,
                self.rect.height + 20,
                duration=2000
            )
            if self.sound_manager:
                self.sound_manager.play('boss_phase_change', 0.7)
        
            # Extended invulnerability during phase transition
            self.temps_invulnerable = self.current_time
            self.vulnerable = False
            self.duree_invulnerabilite = BossConstants.VULNERABILITE_DUREE * 2  # Double duration for transitions
        
        return False

    def die(self):
        self.is_dead = True
        # Add death explosion particles
        self.effect_manager.add_particles(
            self.rect.centerx,
            self.rect.centery,
            num_particles=30,
            color=(255, 165, 0),  # Orange explosion
            particle_type='explosion'
        )

    def draw(self, fenetre):
        if self.is_dead:
            self.effect_manager.draw(fenetre)
            return
            
        # Draw warning/danger zones first
        self.effect_manager.draw(fenetre)
        
        # Draw the boss
        if self.flash_timer > 0:
            fenetre.blit(self.flash_image, self.rect)
        else:
            fenetre.blit(self.image, self.rect)
        
        # Draw active effects
        self.effect_manager.draw(fenetre)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(fenetre)
            
        # Draw health bar
        barre_largeur = self.rect.width
        barre_hauteur = 10
        x = self.rect.x
        y = self.rect.y - 20
        
        # Background (red)
        pygame.draw.rect(fenetre, (255, 0, 0), (x, y, barre_largeur, barre_hauteur))
        # Health (green)
        sante_largeur = max(0, (self.health / self.max_health) * barre_largeur)
        pygame.draw.rect(fenetre, (0, 255, 0), (x, y, sante_largeur, barre_hauteur))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > BossConstants.DELAI_TIR:
            self.last_shot = now
            return True
        return False

    def get_health_percentage(self):
        return (self.health / self.max_health) * 100

    def select_new_pattern(self):
        """Select and start a new movement pattern."""
        if not self.available_patterns:  # Safety check
            return
            
        # Select pattern based on current phase
        patterns = self.available_patterns.get(self.phase, self.available_patterns[1])
        pattern_class = random.choice(patterns)
        
        # Create and start new pattern
        self.current_pattern = pattern_class(self)
        self.current_pattern.start()

    def create_flash_image(self):
        flash = self.original_image.copy()
        flash.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        return flash
