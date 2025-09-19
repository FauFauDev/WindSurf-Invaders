import pygame
import sys
import random
import math
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_p, K_r, K_f
import os

# Import configuration
from config import *

# Import assets
from assets import SoundManager, load_game_images, load_alien_images, load_image
from effects.visual_effects import EffectManager

# Import entities
from entities.player import Joueur
from entities.alien import Envahisseur, FormationAlien, creer_envahisseurs
from entities.boss import Boss
from entities.mystery_alien import MysteryAlien
from entities.projectiles import Projectile, ProjectileAlien, ProjectileMystereAgressif
from entities.powerup import PowerUp, generer_power_up
from entities.explosion import Explosion
from ui.background import ParallaxBackground
from ui.modern_hud import ModernHUD

from ui.menus import dessiner_menu_accueil, handle_menu_event, menu_state

# Import systems
from systems.score import ComboSystem, charger_meilleur_score, sauvegarder_meilleur_score
from systems.level_transition import LevelTransitionManager

from utils.control_settings import ControlSettings

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Initialize random seed using current time
        random.seed()
        
        self.fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
        self.windowed_size = (LARGEUR, HAUTEUR)
        self.render_surface = pygame.Surface((LARGEUR, HAUTEUR)).convert()
        pygame.display.set_caption('Nebula Surge')
        
        self.controls = ControlSettings()
        menu_state.load_resources()

        # Load assets
        self.images = load_game_images()
        self.effect_manager = EffectManager(self.images)
        
        # Use selected ship if available, otherwise use default
        from ui.menus import get_selected_ship
        selected_ship = get_selected_ship()
        if selected_ship:
            self.images['player'] = selected_ship
        
        # Load alien images
        self.alien_images = load_alien_images()  # Load alien images
        
        # Load boss images
        boss_dir = os.path.join(ASSETS_DIR, 'images', 'boss')
        print(f"Looking for boss images in: {boss_dir}")  # Debug print
        boss_files = [f for f in os.listdir(boss_dir) if f.startswith('boss') and f.endswith('.png')]
        boss_files.sort()  # Sort files to ensure consistent loading order
        print(f"Found boss images: {boss_files}")  # Debug print
        
        self.sound_manager = SoundManager()
        
        # Initialize background with random patterns
        self.background = ParallaxBackground()
        self.background.randomize_backgrounds()  # Ensure initial randomization
        
        # Initialize HUD
        self.hud = ModernHUD()
        
        # Game state
        self.running = True
        self.game_state = GameState.NORMAL
        self.pause = False
        self.menu = True
        self.game_over = False
        
        # Initialize game objects
        self.joueur = None
        self.projectiles = []
        self.projectiles_aliens = []
        self.envahisseurs = []
        self.explosions = []
        self.powerups = []
        self.boss = None
        self.mystery_aliens = []  # Changed to list to support multiple aliens
        self.last_mystery_spawn = pygame.time.get_ticks()
        self.mystery_spawn_delay = random.randint(10000, 15000)  # Increased delay between waves
        self.mystery_wave_size = 0  # Current wave size
        
        # Game variables
        self.score = 0
        self.vies = 3
        self.niveau = 1
        self.niveau_termine = False
        self.transition_niveau = False
        self.dernier_temps_niveau = 0
        self.meilleur_score = charger_meilleur_score()
        
        # Systems
        self.combo_system = ComboSystem()
        self.level_transition = LevelTransitionManager()

        # Timed audio events
        self.scheduled_sounds = []
        
        # Powerup timing
        self.dernier_powerup = 0
        self.delai_min_powerup = 10000  # Minimum 10 seconds between powerups

    def demarrer_nouveau_jeu(self):
        """Initialize a new game."""
        self.score = 0
        self.vies = 3
        self.niveau = 1
        self.game_over = False
        self.menu = False
        self.niveau_termine = False
        self.transition_niveau = False
        self.dernier_temps_niveau = pygame.time.get_ticks()
        
        # Reset all game objects
        self.projectiles.clear()
        self.projectiles_aliens.clear()
        self.explosions.clear()
        self.powerups.clear()
        
        # Randomize background for new game
        self.background.randomize_backgrounds()
        
        # Reset mystery alien
        self.mystery_aliens = []  # Changed to list to support multiple aliens
        self.last_mystery_spawn = pygame.time.get_ticks()
        self.mystery_spawn_delay = random.randint(10000, 15000)  # Increased delay between waves
        self.mystery_wave_size = 0  # Current wave size
        
        # Get the selected ship image
        from ui.menus import get_selected_ship
        selected_ship = get_selected_ship()
        if selected_ship:
            self.images['player'] = selected_ship
        
        # Create player with selected ship image
        self.joueur = Joueur(self.sound_manager, player_img=self.images['player'], controls=self.controls)
        self.joueur.rect.centerx = LARGEUR // 2
        self.joueur.rect.bottom = HAUTEUR - 20
        
        # Create aliens for first level
        self.envahisseurs = creer_envahisseurs(self.niveau, self.alien_images)
        self.boss = None
        
        # Reset combo system and start music
        self.combo_system.reset()
        self.sound_manager.play('music', 0.3)  # Start music at lower volume
        self.level_transition.reset()
        self.scheduled_sounds.clear()

    def toggle_fullscreen(self):
        current_flags = self.fenetre.get_flags()
        if current_flags & pygame.FULLSCREEN:
            self.fenetre = pygame.display.set_mode(self.windowed_size)
        else:
            self.windowed_size = self.fenetre.get_size()
            fullscreen_flags = pygame.FULLSCREEN | pygame.SCALED
            try:
                self.fenetre = pygame.display.set_mode((0, 0), fullscreen_flags)
            except pygame.error as error:
                print(f"Falling back to standard fullscreen: {error}")
                self.fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption('Nebula Surge')

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == KEYDOWN:
                fire_key = self.controls.get('fire')

                if self.menu:
                    menu_action = handle_menu_event(event, self.controls)
                    if menu_action == 'start':
                        self.menu = False
                        self.game_over = False
                        self.pause = False
                        menu_state.active_view = 'main'
                        menu_state.awaiting_binding = None
                        menu_state.binding_feedback = ''
                        menu_state.binding_feedback_time = 0
                        menu_state.controls_selection = 0
                        self.demarrer_nouveau_jeu()
                        continue
                    if menu_action == 'quit':
                        self.running = False
                        continue
                    if menu_action == 'handled':
                        continue

                if event.key == K_ESCAPE:
                    if self.menu:
                        self.running = False
                    else:
                        self.menu = True
                        self.game_over = False
                        self.pause = False
                        menu_state.active_view = 'main'
                        menu_state.awaiting_binding = None
                        menu_state.binding_feedback = ''
                        menu_state.binding_feedback_time = 0
                        menu_state.controls_selection = 0

                elif event.key == K_f:
                    self.toggle_fullscreen()

                elif event.key == fire_key and not self.menu:
                    if not self.pause and not self.game_over:
                        self.tirer()
                        self.tirer()

                elif event.key == K_p and not self.menu and not self.game_over:
                    self.pause = not self.pause
                    if self.pause:
                        self.sound_manager.pause_music()
                    else:
                        self.sound_manager.unpause_music()

                elif event.key == K_r and self.game_over:
                    self.game_over = False
                    self.demarrer_nouveau_jeu()


    def tirer(self):
        if self.joueur.shoot():  # Use the player's shoot method instead of peut_tirer
            x = self.joueur.rect.centerx
            y = self.joueur.rect.top
            projectile = Projectile(x, y, self.images['missile'])
            self.projectiles.append(projectile)

    def update(self):
        current_time = pygame.time.get_ticks()
        self.level_transition.update(current_time)
        self._process_scheduled_sounds(current_time)

        if not self.menu and not self.game_over:
            if not self.pause:
                # Update game objects
                self.background.update()
                self.joueur.update()
                self.update_projectiles()
                self.update_aliens()

                # Update mystery aliens
                # Mystery alien wave spawning
                if len(self.mystery_aliens) == 0 and current_time - self.last_mystery_spawn > self.mystery_spawn_delay:
                    self.mystery_wave_size = random.randint(1, 3)  # Random wave size
                    spacing = LARGEUR // (self.mystery_wave_size + 1)  # Even spacing across screen
                    
                    for i in range(self.mystery_wave_size):
                        new_alien = MysteryAlien(self.sound_manager)
                        # Override the random x position to ensure proper spacing
                        new_alien.rect.x = spacing * (i + 1)
                        new_alien.base_x = float(new_alien.rect.x)  # Update base_x for wave movement
                        self.mystery_aliens.append(new_alien)
                    
                    self.last_mystery_spawn = current_time
                    self.mystery_spawn_delay = random.randint(10000, 15000)  # 10-15 seconds between waves
                
                # Update mystery aliens and handle firing
                for alien in self.mystery_aliens[:]:
                    if alien.is_alive:
                        # Update returns True if alien reached bottom
                        if alien.update():
                            self.vies -= 1  # Lose a life
                            # Create explosion at bottom
                            explosion = Explosion(
                                alien.rect.centerx,
                                alien.rect.bottom,
                                self.images['explosions']
                            )
                            self.explosions.append(explosion)
                            if self.sound_manager:
                                self.sound_manager.play('explosion', 0.3)
                            
                            # Check for game over
                            if self.vies <= 0:
                                self.game_over = True
                                if self.score > self.meilleur_score:
                                    self.meilleur_score = self.score
                                    sauvegarder_meilleur_score(self.score)
                                if self.sound_manager:
                                    self.sound_manager.play('gameover', 0.3)
                            else:
                                if self.sound_manager:
                                    self.sound_manager.play('hit', 0.3)
                        
                        # Random firing with increased probability
                        if random.random() < 0.02:  # 2% chance to fire per alien per update
                            # Calculate direction towards player
                            dx = (self.joueur.rect.centerx - alien.rect.centerx)
                            dy = (self.joueur.rect.centery - alien.rect.centery)
                            distance = math.sqrt(dx * dx + dy * dy)
                            distance = max(distance, 1)  # Avoid division by zero
                            
                            # Normalize and scale the direction
                            speed = 5  # Fixed speed for projectiles
                            normalized_dx = (dx / distance) * speed
                            normalized_dy = abs(dy / distance) * speed  # Make sure dy is positive to go down
                            
                            # Select a larger, more visible projectile image
                            projectile_img = pygame.transform.scale(
                                random.choice(self.images['projectile_alien']), 
                                (20, 40)  # Make projectile bigger
                            )
                            
                            projectile = ProjectileMystereAgressif(
                                alien.rect.centerx,
                                alien.rect.bottom,
                                normalized_dx,
                                normalized_dy,
                                projectile_img
                            )
                            self.projectiles_aliens.append(projectile)
                    else:
                        self.mystery_aliens.remove(alien)
                
                # Check collisions with mystery aliens
                for alien in self.mystery_aliens[:]:
                    if not alien.is_alive:
                        continue
                    
                    for projectile in self.projectiles[:]:
                        if alien.rect.colliderect(projectile.rect):
                            points = alien.hit()
                            self.score += points
                            self.combo_system.add_hit()
                            # Create explosion
                            explosion = Explosion(alien.rect.centerx, alien.rect.centery, self.images['explosions'])
                            self.explosions.append(explosion)
                            self.projectiles.remove(projectile)
                
                self.update_explosions()
                self.update_powerups()
                
                # Only update boss if it exists
                if self.boss is not None:
                    try:
                        self.update_boss()
                    except Exception as e:
                        print(f"Error updating boss: {e}")
                        self.boss = None  # Reset boss if there's an error
                
                # Check level completion
                self.check_level_completion()
            
            # Ensure music is playing during gameplay
            if not self.sound_manager.is_playing('music') and not self.pause:
                self.sound_manager.play('music', 0.3)
        
        elif self.menu:
            pass
        
        elif self.game_over:
            pass

    def update_projectiles(self):
        # Update player projectiles
        for projectile in self.projectiles[:]:
            projectile.deplacer()
            if projectile.rect.bottom < 0:
                self.projectiles.remove(projectile)
                self.joueur.precision_tracker.ajouter_tir(False)
                # Reset combo by setting a long time since last kill
                self.combo_system.dernier_kill = 0
        
        # Update alien projectiles
        for projectile in self.projectiles_aliens[:]:
            projectile.deplacer()
            if projectile.rect.top > HAUTEUR:
                self.projectiles_aliens.remove(projectile)
            elif projectile.rect.colliderect(self.joueur.rect) and not self.joueur.est_invincible and not self.joueur.shield_actif:
                self.projectiles_aliens.remove(projectile)
                self.joueur.prendre_degats()
                self.vies -= 1
                if self.vies <= 0:
                    self.game_over = True
                    if self.score > self.meilleur_score:
                        self.meilleur_score = self.score
                        sauvegarder_meilleur_score(self.score)
                    if self.sound_manager:
                        self.sound_manager.play('gameover', 0.3)
                        self.sound_manager.play('music', 0.1)
                else:
                    if self.sound_manager:
                        self.sound_manager.play('hit', 0.3)

    def update_aliens(self):
        # Update alien positions and check for direction changes
        direction_change = False
        current_time = pygame.time.get_ticks()
        
        for alien in self.envahisseurs:
            if isinstance(alien, FormationAlien):
                # Update formation-based movement
                alien.update_formation_position(current_time)
            else:
                # Regular alien movement
                new_x = alien.deplacer()
                if (new_x <= 50 and alien.direction < 0) or \
                   (new_x >= LARGEUR - 50 and alien.direction > 0):
                    direction_change = True
        
        if direction_change:
            # Change direction and move down
            for alien in self.envahisseurs:
                if not isinstance(alien, FormationAlien):
                    alien.direction *= -1
                    if alien.descendre(20):
                        self.game_over = True

        # Make aliens shoot
        for alien in self.envahisseurs:
            if alien.tirer(self.boss is not None):
                projectile = ProjectileAlien(
                    alien.rect.centerx,
                    alien.rect.bottom,
                    self.images['shots'][alien.rangee % 6],
                    alien.type_alien,
                    alien.rangee
                )
                self.projectiles_aliens.append(projectile)
        
        # Move aliens
        move_down = False
        for alien in self.envahisseurs:
            new_x = alien.deplacer()
            if (new_x <= 0 and alien.direction < 0) or (new_x >= LARGEUR - alien.rect.width and alien.direction > 0):
                move_down = True
                break
        
        if move_down:
            for alien in self.envahisseurs:
                alien.direction *= -1
                if alien.descendre(20):  # Returns True if reached bottom
                    self.game_over = True
                    if self.score > self.meilleur_score:
                        self.meilleur_score = self.score
                        sauvegarder_meilleur_score(self.score)
        
        # Check collisions with player projectiles
        for projectile in self.projectiles[:]:
            for alien in self.envahisseurs[:]:
                if projectile.rect.colliderect(alien.rect):
                    if alien.prendre_degats(1):
                        self.envahisseurs.remove(alien)
                        self.score += self.combo_system.obtenir_score(alien.points)
                        self.combo_system.augmenter_combo()
                        
                        # Create explosion
                        explosion = Explosion(
                            alien.rect.centerx,
                            alien.rect.centery,
                            self.images['explosions'],
                            False
                        )
                        self.explosions.append(explosion)
                        self.sound_manager.play('explosion', 0.3)
                        
                        # Maybe spawn powerup
                        if random.random() < CHANCE_POWERUP:
                            powerup = generer_power_up(
                                alien.rect.centerx,
                                alien.rect.centery,
                                self.images
                            )
                            self.powerups.append(powerup)
                    
                    self.projectiles.remove(projectile)
                    break

    def update_boss(self):
        if self.boss is None:
            return
        
        # Update boss position and state
        self.boss.update(self.joueur)  # Pass player object for patterns
        
        # Handle boss shooting
        new_projectiles = self.boss.tirer(self.joueur)  # Pass player object for targeting
        if new_projectiles:
            for pos_x, pos_y, dx, dy in new_projectiles:
                projectile = ProjectileAlien(pos_x, pos_y, random.choice(self.images['projectile_alien']), 3, 0)  # Using type_alien=3 for boss projectiles
                self.projectiles_aliens.append(projectile)
        
        # Check for collisions with player projectiles
        for projectile in self.projectiles[:]:
            if self.boss.rect.colliderect(projectile.rect):
                # Always play boss damage sound on hit
                self.sound_manager.play('boss_damage', 0.85)
                
                # Handle damage and effects
                is_dead = self.boss.prendre_degats(projectile.damage)
                self.projectiles.remove(projectile)
                
                # Create explosion at hit location
                explosion = Explosion(
                    projectile.rect.centerx,
                    projectile.rect.centery,
                    self.images['explosions']
                )
                self.explosions.append(explosion)
                
                if is_dead:
                    # Create big explosion for boss death
                    scaled_images = [pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2)) 
                                   for img in self.images['explosions']]
                    explosion = Explosion(
                        self.boss.rect.centerx,
                        self.boss.rect.centery,
                        scaled_images
                    )
                    self.explosions.append(explosion)
                    self.score += self.boss.points
                    self.sound_manager.play('boss_defeated', 0.7)
                    self.sound_manager.play('level_completed', 0.5)
                    self.boss = None

    def update_explosions(self):
        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)

    def update_powerups(self):
        temps_actuel = pygame.time.get_ticks()
        
        # Update existing powerups
        for powerup in self.powerups[:]:
            powerup.deplacer()
            if powerup.rect.top > HAUTEUR:
                self.powerups.remove(powerup)
            elif powerup.rect.colliderect(self.joueur.rect):
                self.vies = powerup.appliquer(self.joueur, self.vies)
                # Activate powerup effect and play appropriate sound
                self.joueur.activer_powerup(powerup.type)
                if powerup.type == "health":
                    self.sound_manager.play('health', 0.6)
                elif powerup.type == "shield":
                    self.sound_manager.play('shield', 0.6)
                else:
                    self.sound_manager.play('powerup', 0.6)
                self.powerups.remove(powerup)
        
        # Check if we should spawn a new powerup
        if (not self.powerups and 
            temps_actuel - self.dernier_powerup > self.delai_min_powerup and 
            random.random() < CHANCE_POWERUP):
            # Choose a random alien as spawn point
            if self.envahisseurs:
                alien = random.choice(self.envahisseurs)
                powerup = generer_power_up(
                    alien.rect.centerx,
                    alien.rect.centery,
                    self.images
                )
                self.powerups.append(powerup)
                self.dernier_powerup = temps_actuel

    def check_level_completion(self):
        if self.level_transition.is_active:
            return

        if not self.envahisseurs and not self.boss and not self.niveau_termine:
            self.niveau_termine = True
            self.dernier_temps_niveau = pygame.time.get_ticks()
            self.sound_manager.play('level_completed', 0.7)

            next_level = self.niveau + 1
            is_boss_level = next_level % BossConstants.NIVEAU_APPARITION == 0

            self.level_transition.start(
                next_level,
                is_boss_level,
                lambda nl=next_level, boss=is_boss_level: self._prepare_next_stage(nl, boss)
            )

    def _prepare_next_stage(self, next_level, is_boss_level):
        """Set up enemies and state for the upcoming level."""
        self.projectiles.clear()
        self.projectiles_aliens.clear()
        self.explosions.clear()

        self.niveau = next_level
        self.niveau_termine = False
        self.transition_niveau = False
        self.background.randomize_backgrounds()
        self.dernier_temps_niveau = pygame.time.get_ticks()

        # Reset auxiliary spawns so waves feel fresh
        self.mystery_aliens.clear()
        self.last_mystery_spawn = pygame.time.get_ticks()
        self.mystery_wave_size = 0

        if is_boss_level:
            print(f"Starting boss level {self.niveau}")
            self._spawn_boss_level()
        else:
            print(f"Starting normal level {self.niveau}")
            self.boss = None
            self.envahisseurs = creer_envahisseurs(self.niveau, self.alien_images)

    def _spawn_boss_level(self):
        self.envahisseurs = []
        try:
            if 'boss' in self.images and self.images['boss']:
                boss_image = random.choice(self.images['boss'])
                print(f"Creating boss with image size: {boss_image.get_size()}")
                self.boss = Boss(
                    self.niveau // BossConstants.NIVEAU_APPARITION,
                    boss_image,
                    self.images,
                    sound_manager=self.sound_manager
                )
                self.sound_manager.play('boss_transition', 0.6)
                self._schedule_sound('boss_warning', 0.7, 800)
                print("Boss created successfully")
            else:
                print("No boss images found, falling back to normal level")
                self.boss = None
                self.envahisseurs = creer_envahisseurs(self.niveau, self.alien_images)
        except Exception as e:
            print(f"Error creating boss: {e}")
            self.boss = None
            self.envahisseurs = creer_envahisseurs(self.niveau, self.alien_images)

    def _schedule_sound(self, sound_name, volume, delay_ms=0):
        if not self.sound_manager:
            return

        trigger_time = pygame.time.get_ticks() + max(0, int(delay_ms))
        self.scheduled_sounds.append((trigger_time, sound_name, volume))

    def _process_scheduled_sounds(self, current_time):
        if not self.sound_manager:
            self.scheduled_sounds.clear()
            return

        remaining = []
        for trigger_time, sound_name, volume in self.scheduled_sounds:
            if current_time >= trigger_time:
                self.sound_manager.play(sound_name, volume)
            else:
                remaining.append((trigger_time, sound_name, volume))

        self.scheduled_sounds = remaining

    def changer_niveau(self):
        """Change to the next level with background transition."""
        self.niveau += 1
        self.niveau_termine = False
        self.transition_niveau = True
        self.dernier_temps_niveau = pygame.time.get_ticks()
        
        # Randomize background for the new level
        self.background.randomize_backgrounds()
        
        # Reset game state for new level but preserve powerups
        self.projectiles.clear()
        self.projectiles_aliens.clear()
        self.explosions.clear()
        # Don't clear powerups here
        
        # Create new aliens for the level
        self.envahisseurs = creer_envahisseurs(self.niveau, self.alien_images)
        
        # Reset player position
        if self.joueur:
            self.joueur.rect.centerx = LARGEUR // 2
            self.joueur.rect.bottom = HAUTEUR - 10

    def draw(self):
        surface = self.render_surface
        surface.fill((0, 0, 0))

        # Draw background first
        self.background.draw(surface)

        if not self.menu and not self.game_over:
            # Draw game objects
            self.joueur.dessiner(surface)

            # Draw player projectiles
            for projectile in self.projectiles:
                if isinstance(projectile, Projectile):
                    projectile.dessiner(surface)

            # Draw alien projectiles
            for projectile in self.projectiles_aliens:
                if isinstance(projectile, (ProjectileAlien, ProjectileMystereAgressif)):
                    projectile.dessiner(surface)

            for alien in self.envahisseurs:
                alien.dessiner(surface)

            for explosion in self.explosions:
                explosion.dessiner(surface)

            for powerup in self.powerups:
                powerup.dessiner(surface)

            # Draw mystery aliens before boss (so boss appears in front)
            for alien in self.mystery_aliens:
                surface.blit(alien.image, alien.rect)

            if self.boss:
                self.boss.draw(surface)

            # Draw HUD using the new modern HUD
            self.hud.draw(surface, self)

            if self.pause:
                from ui.menus import dessiner_menu_pause
                dessiner_menu_pause(surface)

        elif self.menu:
            dessiner_menu_accueil(surface, self.meilleur_score, self.controls)
        elif self.game_over:
            from ui.menus import dessiner_game_over
            dessiner_game_over(surface, self.score, self.meilleur_score)

        # Overlay any active level transition on top of the scene
        self.level_transition.draw(surface)

        if self.fenetre.get_size() != surface.get_size():
            scaled_surface = pygame.transform.smoothscale(surface, self.fenetre.get_size())
            self.fenetre.blit(scaled_surface, (0, 0))
        else:
            self.fenetre.blit(surface, (0, 0))

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        self.sound_manager.play('music', 0.3)
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
