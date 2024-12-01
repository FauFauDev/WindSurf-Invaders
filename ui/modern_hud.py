import pygame
import math
from config import *
import random

class ModernHUD:
    def __init__(self):
        # Initialize fonts with better sizes for visibility
        self.title_font = pygame.font.Font(None, 64)
        self.main_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        # Score animation
        self.displayed_score = 0
        self.score_velocity = 0
        self.last_score = 0
        self.last_score_time = 0
        
        # Enhanced color scheme
        self.neon_blue = (0, 230, 255)  # Brighter cyan
        self.neon_purple = (200, 50, 255)  # More vibrant purple
        self.neon_green = (50, 255, 100)  # Softer green
        self.neon_orange = (255, 140, 0)  # Vibrant orange
        self.deep_blue = (10, 20, 40, 180)  # Slightly more transparent
        self.highlight = (255, 255, 255)
        self.glass_edge = (100, 200, 255, 60)  # Subtle blue edge glow
        self.neon_red = (255, 0, 0)
        
        # Powerup colors and icons
        self.powerup_colors = {
            "shield": (0, 230, 255),  # Cyan for shield
            "life": (50, 255, 100),   # Green for extra life
            "fire": (255, 140, 0),    # Orange for rapid fire
        }
        self.powerup_icons = {
            "shield": "🛡️",
            "life": "❤️",
            "fire": "⚡"
        }
        
        # HUD Design constants
        self.corner_radius = 20
        self.panel_alpha = 180
        self.glow_strength = 3
        self.max_lives = 3  # Maximum number of lives
        
        # Powerup animation state
        self.powerup_animations = {}  # Store animation state for each powerup
        
    def create_rounded_rect_surface(self, width, height, radius, color):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        return surface
        
    def draw_glowing_text(self, surface, text, position, color, glow_color, font, glow_radius=2):
        # Create multiple layers of glow
        for offset in range(glow_radius, 0, -1):
            alpha = int(255 / (offset + 1))
            glow_color_with_alpha = (*glow_color, alpha)
            for dx, dy in [(x, y) for x in [-offset, 0, offset] for y in [-offset, 0, offset]]:
                if dx == 0 and dy == 0:
                    continue
                glow_surf = font.render(text, True, glow_color_with_alpha)
                surface.blit(glow_surf, (position[0] + dx, position[1] + dy))
        
        # Draw main text
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, position)
        
    def draw_score_section(self, surface, score, high_score, temps):
        # Create glass-like panel
        panel_height = 100
        score_panel = self.create_rounded_rect_surface(300, panel_height, 
                                                     self.corner_radius, self.deep_blue)
        
        # Smooth score animation
        score_diff = score - self.displayed_score
        self.score_velocity += score_diff * 0.1
        self.score_velocity *= 0.8
        self.displayed_score += self.score_velocity
        
        # Draw panel with a subtle gradient
        surface.blit(score_panel, (20, 20))
        
        # Draw scores with neon glow effect
        score_text = f"{int(self.displayed_score):,}"
        high_text = f"BEST: {high_score:,}"
        
        # Pulsing glow effect
        glow_intensity = abs(math.sin(temps / 1000))
        score_glow = tuple(int(c * (0.5 + glow_intensity * 0.5)) for c in self.neon_blue)
        
        self.draw_glowing_text(surface, score_text, (40, 35), 
                             self.highlight, score_glow, self.main_font)
        self.draw_glowing_text(surface, high_text, (40, 75), 
                             self.neon_blue, (0, 100, 150), self.small_font)
        
    def draw_life_orbs(self, surface, game_state):
        temps = pygame.time.get_ticks()  # Get current time for animations
        
        # Panel dimensions and position
        panel_width = 150  # Wider panel for better spacing
        panel_height = 50  # Taller panel for better visibility
        panel_x = LARGEUR - panel_width - 20
        panel_y = 20
        
        # Create a glass panel effect
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Draw glass panel with gradient
        for i in range(panel_height):
            alpha = 160 + int(20 * math.sin(temps / 1000 + i / 20))  # Animated transparency
            color = (20, 30, 40, alpha)
            pygame.draw.line(panel, color, (0, i), (panel_width, i))
            
        # Add panel border glow
        pygame.draw.rect(panel, (*self.neon_blue[:3], 30), panel.get_rect(), border_radius=15)
        pygame.draw.rect(panel, (*self.neon_blue[:3], 60), panel.get_rect(), 2, border_radius=15)
        
        # Calculate orb properties
        orb_size = 20  # Larger orbs
        spacing = 30  # More spacing between orbs
        max_lives = self.max_lives
        total_width = (max_lives * (orb_size + spacing) - spacing)
        start_x = (panel_width - total_width) // 2
        orb_y = panel_height // 2
        
        # Draw the panel
        surface.blit(panel, (panel_x, panel_y))
        
        # Draw life orbs with effects
        for i in range(max_lives):
            orb_x = panel_x + start_x + i * (orb_size + spacing)
            orb_center = (orb_x + orb_size // 2, panel_y + orb_y)
            
            if i < game_state.vies:
                # Active orb with pulse effect
                pulse = math.sin(temps / 500 + i * 1.5) * 0.2 + 0.8
                glow_size = int(orb_size * pulse)
                
                # Draw outer glow
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.neon_blue[:3], 30), 
                                (glow_size, glow_size), glow_size)
                surface.blit(glow_surf, 
                           (orb_center[0] - glow_size, orb_center[1] - glow_size))
                
                # Draw main orb with gradient
                for r in range(orb_size, 0, -2):
                    alpha = 150 if r == orb_size else 255
                    color = (
                        int(self.neon_blue[0] * (r/orb_size) + 255 * (1-r/orb_size)),
                        int(self.neon_blue[1] * (r/orb_size) + 255 * (1-r/orb_size)),
                        int(self.neon_blue[2] * (r/orb_size) + 255 * (1-r/orb_size)),
                        alpha
                    )
                    pygame.draw.circle(surface, color, orb_center, r)
                
                # Add highlight
                highlight_pos = (orb_center[0] - orb_size//4, orb_center[1] - orb_size//4)
                pygame.draw.circle(surface, (255, 255, 255, 150), 
                                highlight_pos, orb_size//4)
            else:
                # Inactive orb (empty)
                pygame.draw.circle(surface, (50, 60, 70, 100), orb_center, orb_size//2)
                pygame.draw.circle(surface, (80, 90, 100, 60), orb_center, orb_size//2, 2)
        
    def draw_modern_powerup(self, surface, powerup_type, temps_restant, temps_max, position):
        """Draw a visually stunning powerup indicator with unique effects for each type"""
        SIZE = 60
        CENTER = (position[0] + SIZE//2, position[1] + SIZE//2)
        
        # Create surface for the powerup indicator
        indicator = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        
        # Initialize animation state
        if powerup_type not in self.powerup_animations:
            self.powerup_animations[powerup_type] = {
                'angle': 0,
                'particles': [],
                'wave': 0,
                'flash': 0
            }
        
        anim = self.powerup_animations[powerup_type]
        anim['angle'] = (anim['angle'] + 2) % 360
        anim['wave'] = (anim['wave'] + 0.1) % (2 * math.pi)
        anim['flash'] = max(0, anim['flash'] - 0.05)
        
        # Calculate progress
        progress = temps_restant / temps_max
        
        # Get base color
        base_color = self.powerup_colors[powerup_type]
        r, g, b = base_color
        
        if powerup_type == "shield":
            # Shield effect: Energy field with rotating particles
            # Draw base shield
            shield_radius = SIZE//2 - 5
            for i in range(3):  # Multiple layers
                wave_offset = math.sin(anim['wave']) * 3
                radius = shield_radius - i * 4 + wave_offset
                alpha = int(150 * (1 - i/3) * progress)
                pygame.draw.circle(indicator, (r, g, b, alpha), (SIZE//2, SIZE//2), radius)
            
            # Draw rotating energy particles
            num_particles = 8
            for i in range(num_particles):
                angle = anim['angle'] + (360/num_particles * i)
                x = SIZE//2 + math.cos(math.radians(angle)) * (shield_radius - 5)
                y = SIZE//2 + math.sin(math.radians(angle)) * (shield_radius - 5)
                particle_size = 3 + math.sin(anim['wave'] + i) * 2
                pygame.draw.circle(indicator, (255, 255, 255, 200), (int(x), int(y)), int(particle_size))
            
        elif powerup_type == "fire":
            # Rapid fire effect: Pulsing energy with lightning
            # Draw energy core
            core_radius = int(SIZE//3 * (1 + math.sin(anim['wave']) * 0.2))
            pygame.draw.circle(indicator, (r, g, b, 150), (SIZE//2, SIZE//2), core_radius)
            
            # Draw lightning bolts
            for i in range(4):
                angle = anim['angle'] + 90 * i
                start_x = SIZE//2 + math.cos(math.radians(angle)) * core_radius
                start_y = SIZE//2 + math.sin(math.radians(angle)) * core_radius
                end_x = SIZE//2 + math.cos(math.radians(angle)) * (SIZE//2)
                end_y = SIZE//2 + math.sin(math.radians(angle)) * (SIZE//2)
                
                # Create lightning effect
                points = [(start_x, start_y)]
                for _ in range(2):
                    prev_x, prev_y = points[-1]
                    mid_x = (prev_x + end_x) / 2 + (random.random() - 0.5) * 10
                    mid_y = (prev_y + end_y) / 2 + (random.random() - 0.5) * 10
                    points.append((mid_x, mid_y))
                points.append((end_x, end_y))
                
                # Draw lightning
                alpha = int(200 * progress)
                pygame.draw.lines(indicator, (r, g, b, alpha), False, points, 2)
        
        # Add glow effect based on progress
        glow_surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        glow_radius = int(SIZE//2 + math.sin(anim['wave']) * 5)
        pygame.draw.circle(glow_surf, (*base_color, 30), (SIZE//2, SIZE//2), glow_radius)
        indicator.blit(glow_surf, (0, 0))
        
        # Draw to main surface
        surface.blit(indicator, position)
        
    def draw(self, surface, game_state):
        temps = pygame.time.get_ticks()
        
        # Draw score section
        self.draw_score_section(surface, game_state.score, game_state.meilleur_score, temps)
        
        # Draw life orbs
        self.draw_life_orbs(surface, game_state)
        
        # Calculate center positions for powerups
        center_x = LARGEUR // 2
        powerup_y = 60
        shield_x = center_x - 40
        fire_x = center_x + 40
        
        # Draw powerup indicators
        if game_state.joueur.shield_actif:
            temps_restant = max(0, game_state.joueur.shield_duree - 
                              (temps - game_state.joueur.shield_temps))
            if temps_restant > 0:
                self.draw_modern_powerup(surface, "shield", temps_restant,
                                      game_state.joueur.shield_duree,
                                      (shield_x - 30, powerup_y - 30))
        
        if game_state.joueur.rapid_fire:
            temps_restant = max(0, game_state.joueur.rapid_fire_duration -
                              (temps - game_state.joueur.rapid_fire_timer))
            if temps_restant > 0:
                self.draw_modern_powerup(surface, "fire", temps_restant,
                                      game_state.joueur.rapid_fire_duration,
                                      (fire_x - 30, powerup_y - 30))
        
        # Draw combo indicator
        self.draw_combo_indicator(surface, game_state.combo_system, temps)

    def draw_combo_indicator(self, surface, combo_system, temps):
        if combo_system.combo_count > 0:
            combo_x = LARGEUR - 280
            combo_y = HAUTEUR - 120
            
            # Create glass panel for combo
            combo_panel = self.create_rounded_rect_surface(260, 100, 
                                                         self.corner_radius, self.deep_blue)
            surface.blit(combo_panel, (combo_x, combo_y))
            
            # Calculate combo color based on multiplier
            if combo_system.multiplicateur >= 3.0:
                color = self.neon_purple
                glow = (150, 0, 255)
            elif combo_system.multiplicateur >= 2.0:
                color = (255, 165, 0)  # Neon orange
                glow = (150, 100, 0)
            else:
                color = self.neon_green
                glow = (0, 150, 100)
            
            # Draw combo text with pulsing effect
            pulse = abs(math.sin(temps/200))
            combo_text = f"COMBO x{combo_system.combo_count}"
            
            self.draw_glowing_text(surface, combo_text, 
                                 (combo_x + 20, combo_y + 20),
                                 self.highlight, color, self.main_font)
            
            # Draw combo timer bar
            if combo_system.dernier_kill > 0:
                remaining = 1 - (temps - combo_system.dernier_kill) / combo_system.combo_timeout
                if remaining > 0:
                    bar_width = 220
                    bar_height = 10
                    progress = bar_width * remaining
                    
                    # Draw background bar
                    pygame.draw.rect(surface, (40, 40, 60),
                                   (combo_x + 20, combo_y + 70, bar_width, bar_height),
                                   border_radius=5)
                    
                    # Draw progress with glow
                    for i in range(2):
                        bar_alpha = 255 if i == 0 else 128
                        bar_offset = i * 2
                        pygame.draw.rect(surface, (*color, bar_alpha),
                                       (combo_x + 20, combo_y + 70 - bar_offset, 
                                        progress, bar_height + bar_offset * 2),
                                       border_radius=5)

    def draw_menu(self, surface, game_state):
        temps = pygame.time.get_ticks()
        center_x = LARGEUR // 2

        # Draw "WINDSURF INVADERS" title higher up with enhanced glow
        title_y = HAUTEUR // 6  # Moved higher up (was HAUTEUR//4)
        title_text = "WINDSURF INVADERS"
        title_font = pygame.font.Font(None, 128)  # Larger font size
        pulse = abs(math.sin(temps/1000)) * 0.5 + 0.5
        title_glow = tuple(int(c * pulse) for c in self.neon_purple)
        self.draw_glowing_text(surface, title_text,
                             (center_x - title_font.size(title_text)[0]//2, title_y),
                             self.highlight, title_glow, title_font, glow_radius=4)

        # Draw "HIGH SCORE" with enhanced glass panel and animated glow
        score_y = title_y + 150  # Increased spacing from title
        score_panel = self.create_rounded_rect_surface(500, 120, self.corner_radius, self.deep_blue)
        score_x = center_x - 250
        surface.blit(score_panel, (score_x, score_y))
        
        score_title = "HIGH SCORE"
        score_value = f"{game_state.meilleur_score:,}"
        score_glow = tuple(int(c * pulse) for c in self.neon_blue)
        
        # Draw high score title with larger font and better spacing
        title_font = pygame.font.Font(None, 72)  # Larger font for HIGH SCORE
        self.draw_glowing_text(surface, score_title,
                             (center_x - title_font.size(score_title)[0]//2, score_y + 20),
                             self.neon_blue, score_glow, title_font)
        self.draw_glowing_text(surface, score_value,
                             (center_x - self.main_font.size(score_value)[0]//2, score_y + 70),
                             self.highlight, score_glow, self.main_font)

        # Draw "SELECT YOUR SHIP" with enhanced design
        select_y = score_y + 200  # Increased spacing from high score
        select_text = "SELECT YOUR SHIP"
        select_panel = self.create_rounded_rect_surface(600, 100, self.corner_radius, self.deep_blue)
        select_x = center_x - 300
        surface.blit(select_panel, (select_x, select_y))
        
        # Draw select ship text with larger font and better spacing
        select_font = pygame.font.Font(None, 72)  # Larger font for SELECT YOUR SHIP
        select_glow = tuple(int(c * pulse) for c in self.neon_orange)
        self.draw_glowing_text(surface, select_text,
                             (center_x - select_font.size(select_text)[0]//2, select_y + 30),
                             self.neon_orange, select_glow, select_font)

        # Draw "PRESS SPACE TO START" at the bottom
        start_text = "PRESS SPACE TO START"
        start_y = HAUTEUR - 150  # Keep at bottom
        start_glow = tuple(int(c * pulse) for c in self.neon_green)
        self.draw_glowing_text(surface, start_text,
                             (center_x - self.main_font.size(start_text)[0]//2, start_y),
                             self.neon_green, start_glow, self.main_font)
