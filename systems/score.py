import pygame
import json
import os
import shutil
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SCORE_FILE = os.path.join(DATA_DIR, 'highscore.json')
BACKUP_FILE = os.path.join(DATA_DIR, 'highscore.backup.json')
MAX_VALID_SCORE = 999999999  # 1 billion - 1

def ensure_data_directory():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except OSError as e:
            logger.error(f"Failed to create data directory: {e}")
            raise

def validate_score(score):
    """Validate if a score is legitimate"""
    if not isinstance(score, (int, float)):
        return False
    if score < 0 or score > MAX_VALID_SCORE:
        return False
    return True

def backup_score_file():
    """Create a backup of the score file"""
    if os.path.exists(SCORE_FILE):
        try:
            shutil.copy2(SCORE_FILE, BACKUP_FILE)
        except OSError as e:
            logger.error(f"Failed to create backup: {e}")

def restore_from_backup():
    """Attempt to restore score from backup file"""
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, 'r') as f:
                data = json.load(f)
                if 'highscore' in data and validate_score(data['highscore']):
                    return data['highscore']
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to restore from backup: {e}")
    return 0

def charger_meilleur_score():
    """Load the high score with improved error handling and backup restoration"""
    ensure_data_directory()
    
    try:
        # Try to load from main file
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                score = data.get('highscore', 0)
                if validate_score(score):
                    return score
                logger.warning("Invalid score found in save file")
        
        # If main file fails, try backup
        return restore_from_backup()
    
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.error(f"Error loading high score: {e}")
        return 0

def sauvegarder_meilleur_score(score):
    """Save the high score with validation and backup"""
    if not validate_score(score):
        logger.error(f"Attempted to save invalid score: {score}")
        return False
        
    ensure_data_directory()
    backup_score_file()
    
    try:
        data = {
            'highscore': score,
            'timestamp': time.time(),
            'version': '1.0'
        }
        
        with open(SCORE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    
    except OSError as e:
        logger.error(f"Failed to save high score: {e}")
        return False

class ComboSystem:
    def __init__(self):
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.multiplicateur = 1.0
        self.font = pygame.font.Font(None, 36)
        self.derniere_augmentation = pygame.time.get_ticks()
        self.flash_alpha = 0
        self.dernier_kill = pygame.time.get_ticks()
        self.combo_count = 0
        self.combo_timeout = 2000
        self.flash_combo = False
        self.temps_flash = 0
        self.duree_flash = 500
        self.ancien_multiplicateur = 1.0
        self.position_y_offset = 0
        self.espace_texte = 120

    def add_hit(self):
        """Add a hit to the combo system and update the multiplier"""
        current_time = pygame.time.get_ticks()
        
        # Reset combo if too much time has passed since last hit
        if current_time - self.dernier_kill > self.combo_timeout:
            self.combo_count = 0
            self.multiplicateur = 1.0
        
        # Increment combo count and update multiplier
        self.combo_count += 1
        if self.combo_count > 1:  # Start increasing multiplier after first hit
            self.multiplicateur = min(2.0, 1.0 + (self.combo_count - 1) * 0.1)  # Cap at 2.0x
        
        # Update timing
        self.dernier_kill = current_time
        self.flash_alpha = 255  # Flash effect for visual feedback

    def augmenter_combo(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.dernier_kill < self.combo_timeout:
            self.combo_count += 1
            self.ancien_multiplicateur = self.multiplicateur
            
            if self.combo_count >= 7:
                self.multiplicateur = 3.0
            elif self.combo_count >= 5:
                self.multiplicateur = 2.0
            elif self.combo_count >= 3:
                self.multiplicateur = 1.5
            
            if self.multiplicateur > self.ancien_multiplicateur:
                self.activer_flash()
        else:
            self.combo_count = 1
            self.multiplicateur = 1.0
        
        self.dernier_kill = current_time

    def activer_flash(self):
        self.flash_combo = True
        self.temps_flash = pygame.time.get_ticks()
        self.flash_alpha = 255
        self.position_y_offset = -20

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update combo timeout
        if current_time - self.dernier_kill > self.combo_timeout:
            self.combo_count = 0
            self.multiplicateur = 1.0
        
        # Update flash effect
        if self.flash_combo:
            temps_ecoule = current_time - self.temps_flash
            if temps_ecoule < self.duree_flash:
                self.flash_alpha = int(255 * (1 - temps_ecoule / self.duree_flash))
                self.position_y_offset = -20 * (1 - temps_ecoule / self.duree_flash)
            else:
                self.flash_combo = False
                self.flash_alpha = 0
                self.position_y_offset = 0

    def obtenir_score(self, points_base):
        return int(points_base * self.multiplicateur)

    def dessiner(self, fenetre, x, y):
        if self.multiplicateur > 1.0:
            self.dessiner_multiplicateur(fenetre, x, y, self.multiplicateur)
            if self.flash_combo:
                self.dessiner_multiplicateur(
                    fenetre,
                    x,
                    y + self.position_y_offset,
                    self.multiplicateur,
                    self.flash_alpha
                )

    def dessiner_multiplicateur(self, surface, x, y, valeur, alpha=255):
        texte = f'x{valeur:.1f}'
        couleur = (255, 255, 0, alpha)  # Yellow with alpha
        
        # Create a surface for the text with alpha channel
        font_surface = self.font.render(texte, True, couleur)
        alpha_surface = pygame.Surface(font_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((255, 255, 255, alpha))
        font_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Calculate position
        rect = font_surface.get_rect()
        rect.centerx = x + self.espace_texte
        rect.centery = y
        
        # Draw the text
        surface.blit(font_surface, rect)

    def reset(self):
        """Reset the combo system to its initial state"""
        self.multiplicateur = 1.0
        self.derniere_augmentation = pygame.time.get_ticks()
        self.flash_alpha = 0
        self.dernier_kill = pygame.time.get_ticks()
        self.combo_count = 0
        self.flash_combo = False
        self.temps_flash = 0
        self.position_y_offset = 0
        self.ancien_multiplicateur = 1.0
