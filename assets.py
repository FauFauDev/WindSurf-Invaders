import pygame
import os
import logging
from config import ASSETS_DIR, LARGEUR, HAUTEUR

logger = logging.getLogger('space_invaders')

def load_image(path):
    """Load an image and convert it to the right format for PyGame."""
    try:
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning)
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        logger.error(f"Impossible de charger l'image {path}: {e}")
        raise SystemExit

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)  # Ensure we have enough channels
        self.sounds = {}
        self.music_channel = pygame.mixer.Channel(0)  # Reserve channel 0 for music
        self.music_playing = False
        self.music_paused = False
        self.channel_warning = pygame.mixer.Channel(1)  # Dedicated channel for warning sound
        # Default volume levels for different sound categories
        self.volume_levels = {
            'music': 0.5,      # Background music at 50% volume
            'shoot': 0.4,      # Player shooting at 40% volume
            'explosion': 0.6,  # Explosions at 60% volume
            'shield': 0.5,     # Shield effects at 50% volume
            'health': 0.5,     # Health pickup at 50% volume
            'boss': 0.7,       # Boss appear sound at 70% volume
            'gameover': 0.7,   # Game over at 70% volume
            'level_completed': 0.7,  # Level completion at 70% volume
            'warning': 0.6,    # Warning sound at 60% volume
            'boss_transition': 0.7,  # Boss transition at 70% volume
            'boss_defeated': 0.7,     # Boss defeated at 70% volume
            'boss_damage': 0.85,      # Increased boss damage volume to 85%
            'boss_phase_change': 0.7, # Boss phase change at 70% volume
            'powerup': 0.7,           # Powerup at 70% volume
            'game_over': 0.7          # Game over at 70% volume
        }
        self.load_sounds()

    def load_sounds(self):
        sound_dir = os.path.join(ASSETS_DIR, 'sounds')
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav',
            'hit': 'explosion.wav',  # Use explosion sound for hits
            'powerup': 'health.wav',  # Use health sound for powerups
            'health': 'health.wav',
            'shield': 'shield.wav',
            'boss_damage': 'boss_damage.wav',
            'boss_transition': 'boss_transition.wav',
            'boss_defeated': 'boss_defeated.wav',
            'boss_warning': 'warning.wav',  # Renamed from 'boss' to 'boss_warning'
            'warning': 'warning.wav',
            'level_completed': 'LevelCompleted.wav',
            'gameover': 'gameover.wav',  # Fixed name to match file
            'game_over': 'gameover.wav',  # Alternative name mapping to same file
            'boss_phase_change': 'boss_phase_change.wav',
            'music': 'music.wav'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                sound_path = os.path.join(sound_dir, filename)
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    print(f"Loaded sound: {sound_name} from {sound_path}")  # Debug print
                else:
                    print(f"Warning: Sound file not found: {sound_path}")
            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
                
    def play(self, sound_name, volume=None, loop=False):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            # Use provided volume or fall back to the default category volume
            if volume is not None:
                actual_volume = volume
            else:
                actual_volume = self.volume_levels.get(sound_name, 0.5)
            sound.set_volume(actual_volume)
            
            # Special handling for warning sound
            if sound_name == 'warning':
                if loop:
                    self.channel_warning.play(sound, -1)  # -1 means loop indefinitely
                else:
                    self.channel_warning.play(sound, 0)  # Play once
                self.channel_warning.set_volume(volume)
            # Handle music specially on the dedicated music channel
            elif sound_name == 'music':
                if not self.music_playing and not self.music_paused:
                    self.music_channel.play(sound, loops=-1)  # Loop indefinitely
                    self.music_playing = True
                    self.music_channel.set_volume(actual_volume)
            else:
                # For other sounds, play immediately
                sound.play()
        else:
            print(f"Warning: Sound not found: {sound_name}")

    def set_volume(self, sound_name, volume):
        """Set volume for a specific sound category"""
        if 0.0 <= volume <= 1.0:
            self.volume_levels[sound_name] = volume
            if sound_name in self.sounds:
                self.sounds[sound_name].set_volume(volume)
            if sound_name == 'music' and self.music_playing:
                self.music_channel.set_volume(volume)

    def get_volume(self, sound_name):
        """Get current volume for a specific sound category"""
        return self.volume_levels.get(sound_name, 0.5)

    def stop(self, sound_name=None):
        if sound_name:
            if sound_name == 'music':
                self.music_channel.stop()
                self.music_playing = False
                self.music_paused = False
            elif sound_name == 'warning':
                self.channel_warning.stop()
            elif sound_name in self.sounds:
                self.sounds[sound_name].stop()
        else:
            self.music_channel.stop()
            self.music_playing = False
            self.music_paused = False
            self.channel_warning.stop()
            for sound in self.sounds.values():
                sound.stop()

    def pause_music(self):
        if self.music_playing:
            self.music_channel.pause()
            self.music_paused = True

    def unpause_music(self):
        if self.music_paused:
            self.music_channel.unpause()
            self.music_paused = False
            self.music_playing = True

    def is_playing(self, sound_name):
        if sound_name == 'music':
            return self.music_playing and not self.music_paused
        elif sound_name == 'warning':
            return self.channel_warning.get_busy()
        return False

def load_game_images():
    images = {}
    
    # Load player image
    images['player'] = load_image(os.path.join(ASSETS_DIR, 'images', 'player.png'))
    images['player'] = pygame.transform.scale(images['player'], (64, 80))
    
    # Load alien images
    images['aliens'] = load_alien_images()
    
    # Load effects images
    effects_dir = os.path.join(ASSETS_DIR, 'images', 'effects')
    images['effects'] = {}
    if os.path.exists(effects_dir):
        effects_files = {
            'damage': 'damage_particle.png',
            'danger': 'danger_zone.png',
            'particle': 'particle.png',
            'phase': 'phase_transition.png',
            'teleport': 'teleport_particle.png',
            'warning': 'warning.png'
        }
        
        for effect_name, filename in effects_files.items():
            try:
                img_path = os.path.join(effects_dir, filename)
                if os.path.exists(img_path):
                    images['effects'][effect_name] = load_image(img_path)
                    print(f"Successfully loaded effect image: {filename}")
                else:
                    print(f"Warning: Effect image not found: {img_path}")
            except Exception as e:
                print(f"Error loading effect image {filename}: {e}")
    else:
        print(f"Warning: Effects images directory not found: {effects_dir}")
    
    # Load boss images
    images['boss'] = []
    boss_dir = os.path.join(ASSETS_DIR, 'images', 'boss')
    if os.path.exists(boss_dir):
        boss_files = [f for f in os.listdir(boss_dir) if f.startswith('boss') and f.endswith('.png')]
        boss_files.sort()  # Sort files to ensure consistent loading order
        print(f"Loading boss images from: {boss_dir}")
        print(f"Found boss images: {boss_files}")
        
        if not boss_files:
            print("Warning: No boss image files found in", boss_dir)
        
        for boss_file in boss_files:
            try:
                img_path = os.path.join(boss_dir, boss_file)
                if not os.path.exists(img_path):
                    print(f"Warning: Boss image file not found: {img_path}")
                    continue
                    
                img = load_image(img_path)
                if img is None:
                    print(f"Warning: Failed to load boss image: {boss_file}")
                    continue
                    
                # Pre-scale the boss images to the correct size
                img = pygame.transform.scale(img, (200, 200))  # Using BossConstants.TAILLE
                images['boss'].append(img)
                print(f"Successfully loaded and scaled boss image: {boss_file}")
            except Exception as e:
                print(f"Error loading boss image {boss_file}: {e}")
        
        print(f"Successfully loaded {len(images['boss'])} boss images")
    else:
        print(f"Warning: Boss images directory not found: {boss_dir}")
    
    # Load shots images
    images['shots'] = []
    for i in range(1, 7):
        img = load_image(os.path.join(ASSETS_DIR, 'images', 'shots', f'shot{i}.png'))
        img = pygame.transform.scale(img, (20, 20))
        img_rotated = pygame.transform.rotate(img, -90)
        images['shots'].append(img_rotated)

    # Load projectile images
    images['projectile'] = load_image(os.path.join(ASSETS_DIR, 'images', 'missile.png'))
    images['projectile_alien'] = []
    for i in range(1, 7):
        img = load_image(os.path.join(ASSETS_DIR, 'images', 'shots', f'shot{i}.png'))
        img = pygame.transform.scale(img, (20, 20))
        img_rotated = pygame.transform.rotate(img, -90)
        images['projectile_alien'].append(img_rotated)
    
    # Load missile image
    images['missile'] = load_image(os.path.join(ASSETS_DIR, 'images', 'missile.png'))
    images['missile'] = pygame.transform.scale(images['missile'], (images['missile'].get_width(), images['missile'].get_height()))
    
    # Load powerups images
    images['powerups'] = {}
    powerup_types = ['shield', 'life', 'fire']
    for powerup in powerup_types:
        img = load_image(os.path.join(ASSETS_DIR, 'images', 'powerup', f'{powerup}.png'))
        img = pygame.transform.scale(img, (60, 60))
        images['powerups'][powerup] = img

    # Load explosion images
    images['explosions'] = []
    for i in range(1, 7):
        img = load_image(os.path.join(ASSETS_DIR, 'images', 'explosions', f'explosion{i}.png'))
        img = pygame.transform.scale(img, (128, 128))
        images['explosions'].append(img)
    
    return images

def load_alien_images():
    alien_images = []
    for i in range(1, 7):
        img = load_image(os.path.join(ASSETS_DIR, 'images', 'aliens', f'Ship{i}.png'))
        img = pygame.transform.scale(img, (64, 64))
        alien_images.append(img)
    return alien_images

def load_backgrounds():
    backgrounds = []
    backgrounds_dir = os.path.join('assets', 'backgrounds')  # Changed to relative path
    
    try:
        # Load and scale all background images
        for fichier in sorted(os.listdir(backgrounds_dir)):
            if fichier.endswith('.png') and ('Nebula' in fichier):  # Only load Nebula backgrounds
                try:
                    image = load_image(os.path.join(backgrounds_dir, fichier))
                    image = pygame.transform.scale(image, (LARGEUR, HAUTEUR))
                    
                    # Create a darker version for the parallax effect
                    dark_image = image.copy()
                    dark_overlay = pygame.Surface((LARGEUR, HAUTEUR))
                    dark_overlay.fill((0, 0, 0))
                    dark_overlay.set_alpha(100)
                    dark_image.blit(dark_overlay, (0, 0))
                    
                    backgrounds.append({
                        'main': image,
                        'dark': dark_image,
                        'scroll_speed': 0.5 + len(backgrounds) * 0.25  # Each layer scrolls faster
                    })
                except Exception as e:
                    print(f"Skipping background {fichier}: {e}")
                    continue
    except Exception as e:
        print(f"Error loading backgrounds: {e}")
        # Return at least one empty background as fallback
        empty_bg = pygame.Surface((LARGEUR, HAUTEUR))
        empty_bg.fill((0, 0, 0))  # Black background
        backgrounds.append({
            'main': empty_bg,
            'dark': empty_bg.copy(),
            'scroll_speed': 0.5
        })
    
    return backgrounds

def charger_images():
    images = {
        'vaisseau': pygame.image.load('assets/images/vaisseau.png').convert_alpha(),
        'aliens': [
            pygame.image.load(f'assets/images/alien{i}.png').convert_alpha()
            for i in range(1, 4)
        ],
        'projectile': pygame.image.load('assets/images/projectile.png').convert_alpha(),
        'projectile_alien': pygame.image.load('assets/images/projectile_alien.png').convert_alpha(),
        'explosion': [
            pygame.image.load(f'assets/images/explosion{i}.png').convert_alpha()
            for i in range(1, 6)
        ],
        'powerup': pygame.image.load('assets/images/powerup.png').convert_alpha(),
        # Removed default boss image - now using random boss images from assets/images/boss folder
        'backgrounds': [
            {
                'main': pygame.image.load('assets/images/background_stars.png').convert_alpha(),
                'dark': pygame.Surface((LARGEUR, HAUTEUR)),
                'scroll_speed': 0.5
            },
            {
                'main': pygame.image.load('assets/images/background_nebula.png').convert_alpha(),
                'dark': pygame.Surface((LARGEUR, HAUTEUR)),
                'scroll_speed': 1.0
            },
            {
                'main': pygame.image.load('assets/images/background_planets.png').convert_alpha(),
                'dark': pygame.Surface((LARGEUR, HAUTEUR)),
                'scroll_speed': 1.5
            }
        ]
    }
    
    # Create dark overlays for backgrounds
    for bg in images['backgrounds']:
        bg['dark'].fill((0, 0, 0))
        bg['dark'].set_alpha(128)
    
    return images
