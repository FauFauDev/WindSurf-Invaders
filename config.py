import os
import pygame
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_r,
    K_p,
    K_ESCAPE,  
    QUIT,
    KEYDOWN
)

# Window Configuration
LARGEUR = 1600
HAUTEUR = 1200
HUD_HAUTEUR = 60

# Colors
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)

# Gameplay Parameters
VITESSE_ALIEN = 1
VITESSE_ALIEN_POST_BOSS = 1.5  # Speed multiplier after boss fight
VITESSE_DESCENTE = 20
FREQUENCE_TIR_ALIEN_BASE = 0.0003
FREQUENCE_TIR_REDUCTION_BOSS = 0.5
DELAI_ENTRE_TIRS = 1000
DELAI_ENTRE_TIRS_JOUEUR = 300
DELAI_ENTRE_TIRS_JOUEUR_RAPIDE = 150
VITESSE_PROJECTILE_ALIEN = 2
BONUS_POINTS_NIVEAU = 1000
CHANCE_POWERUP = 0.1
VIES_MAX = 3

# Combo System
COMBOS_POINTS = {
    3: 1.5,
    5: 2.0,
    7: 3.0
}
COMBO_TEMPS_MAX = 2000

# Asset Directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Boss Constants
class BossConstants:
    NIVEAU_APPARITION = 2
    HP_BASE = 50  # Reduced from 80 to 50 for faster first encounter
    HP_NIVEAU_MULTIPLIER = 0.15  # Reduced from 0.2 to 0.15 for more gradual scaling
    TAILLE = (200, 200)
    VITESSE_BASE = 2
    POINTS = 1000
    DELAI_TIR = 2000
    VULNERABILITE_DUREE = 1000
    PHASE_THRESHOLD = 0.7  # 70% health for phase 2
    PHASE_3_THRESHOLD = 0.3  # 30% health for phase 3
    RAGE_THRESHOLD = 0.3
    
    # Health and damage
    MAX_HEALTH = 1000
    DAMAGE = 10
    DAMAGE_RESISTANCE = 0.85  # Increased damage taken (was 0.7)
    SPEED = 3
    MIN_Y = 100
    MAX_Y = 300
    AMPLITUDE_Y = 50
    
    # Pattern system
    PATTERN_DURATION = 5000  # 5 seconds per pattern
    PATTERN_COOLDOWN = 1000  # 1 second between patterns
    SPIRAL_RADIUS = 200
    BERSERK_SPEED_MULTIPLIER = 2.0
    
    # Combat
    SHOT_COOLDOWN = 1000  # 1 second between shots
    
    # Visual effects
    WARNING_DURATION = 1000
    WARNING_ALPHA = 128
    DANGER_ZONE_DURATION = 2000
    PARTICLE_LIFETIME = 1000
    TRANSITION_DURATION = 2000
    
    # Pattern timings
    DASH_COOLDOWN = 3000
    TELEPORT_COOLDOWN = 4000
    FLASH_DURATION = 200
    
    # Movement constants
    DASH_SPEED_MULTIPLIER = 3.0
    SPIRAL_SPEED = 0.1
    
    # Attack constants
    PROJECTILE_BASE_SPEED = 5
    BURST_SIZE = 5
    SUMMON_COOLDOWN = 15000  # Time between summoning mini-bosses

# Game States
class GameState:
    NORMAL = "normal"
    BOSS_WARNING = "boss_warning"
    BOSS_TRANSITION = "boss_transition"
    BOSS_FIGHT = "boss_fight"
