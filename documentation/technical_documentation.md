# Space Invaders Technical Documentation

## Project Structure

### Core Components
- `main.py`: Main game loop and initialization
- `assets.py`: Asset loading and management
- `config.py`: Game configuration and constants
- `create_effects.py`: Visual effects generation
- `create_sounds.py`: Sound effects management
- `download_assets.py`: Asset downloading utility
- `entities/`: Game entity classes
  * `alien.py`: Alien enemies and formations
  * `boss.py`: Boss enemy behavior
  * `mystery_alien.py`: Special mystery aliens
  * `player.py`: Player character
  * `powerup.py`: Power-up items
  * `projectiles.py`: Projectile management
  * `explosion.py`: Explosion effects
- `effects/`: Visual and gameplay effects
  * `visual_effects.py`: Visual effect management
  * `powerup_effects.py`: Power-up effect implementation
- `systems/`: Game systems
  * `score.py`: Score and combo system
- `ui/`: User interface components
  * `background.py`: Parallax background
  * `menus.py`: Game menus
  * `hud.py`: Heads-up display
  * `modern_hud.py`: Enhanced HUD implementation
- `utils/`: Utility functions
  * `assets_loader.py`: Asset loading utilities
- `data/`: Game data storage
  * `highscore.json`: High score data
  * `highscore.backup.json`: Backup of high scores

## Class Architecture

### Main Game Classes

#### Player Class
```python
class Player(pygame.sprite.Sprite):
    - Controls player movement and shooting
    - Manages player state and collision detection
    - Properties:
        * speed: Movement speed
        * bounce: Visual bounce effect
        * gun_offset: Bullet spawn position
    - Methods:
        * move(): Handles horizontal movement
        * gunpos(): Calculates bullet spawn position
```

#### Alien Class
```python
class Alien(pygame.sprite.Sprite):
    - Manages alien behavior and animation
    - Properties:
        * speed: Movement speed
        * animcycle: Animation timing
        * facing: Movement direction
    - Methods:
        * update(): Handles movement and animation
```

#### Shot/Bomb Classes
```python
class Shot/Bomb(pygame.sprite.Sprite):
    - Manages projectile behavior
    - Properties:
        * speed: Vertical movement speed
    - Methods:
        * update(): Handles movement and bounds checking
```

### Enemy Formation System

#### Formation Types
1. Triangle Formation
   - 5 rows increasing in size from top to bottom
   - Each row has 2 more aliens than the previous (starting with 3)
   - Front row aliens shoot 50% more frequently
   - Spacing: 60 pixels between aliens
   - Points increase based on row position (higher rows = more points)

2. Circle Formation
   - Double circle pattern with inner (8 aliens) and outer (12 aliens) rings
   - Outer circle aliens shoot 30% more frequently
   - Orbital movement around center point
   - Synchronized rotation with time-based angle calculation
   - Dynamic shooting patterns based on position in formation

3. Wave Formation
   - 3 rows of 6 aliens (18 total)
   - Sinusoidal movement pattern
   - Shooting frequency increases at wave peaks/troughs
   - Phase calculated based on column position
   - Wave amplitude varies with time
   - Side-to-side movement while maintaining wave pattern

#### Formation Alien Class
```python
class FormationAlien:
    - Inherits from base Alien class
    - Properties:
        * formation_id: 'triangle', 'circle', or 'wave'
        * position_in_formation: Position data tuple
        * formation_offset: Current position offset
        * movement_speed: Base speed * formation multiplier
    - Methods:
        * update_formation_position(): Updates position based on formation type
        * tirer(): Formation-specific shooting behavior
```

#### Position Data Structure
- Triangle Formation: (row, column, total_columns)
- Circle Formation: (index, total_aliens, 'inner'/'outer')
- Wave Formation: (row, column, total_columns)

#### Formation Generation
```python
def creer_envahisseurs():
    - Randomly selects formation type
    - Creates appropriate number of aliens for formation
    - Sets initial positions and spacing
    - Falls back to classic formation if needed
    - Adjusts for post-boss difficulty
```

#### Shooting Mechanics
- Base shooting chance scaled with level
- Formation-specific modifiers:
  * Triangle: Front row +50% chance
  * Circle: Outer ring +30% chance
  * Wave: +50% at peaks/troughs
- Additional modifiers during boss fights
- Cooldown between shots (1 second)

### Enemy System

#### Mystery Alien Class
```python
class MysteryAlien:
    - Properties:
        * movement_pattern: 'wave', 'zigzag', or 'circular'
        * speed: Random value between 1-2
        * amplitude: Random value between 100-200 (movement range)
        * is_alive: Tracks alien's active state
    - Methods:
        * update(): Updates position and returns True if reached bottom
        * hit(): Handles collision with player projectile
```

#### Movement Patterns
1. Wave Movement
   - Sinusoidal vertical descent
   - Uses sine function for horizontal movement
   - Amplitude determines wave width
   - Speed * 0.5 for vertical movement

2. Zigzag Movement
   - Alternating left-right movement
   - Constant vertical descent
   - Direction changes at amplitude bounds
   - Speed * 2 for horizontal movement

3. Circular Movement
   - Spiral-like descent pattern
   - Uses cosine function for horizontal movement
   - Slower vertical speed (0.3 multiplier)
   - Continuous rotation effect

#### Game Integration
```python
class Game:
    - Mystery Alien Management:
        * mystery_aliens: List of active mystery aliens
        * mystery_wave_size: Random number (1-3) of aliens per wave
        * mystery_spawn_delay: 10-15 seconds between waves
    - Life System Integration:
        * Checks for aliens reaching bottom
        * Triggers life loss and explosions
        * Handles game over condition
```

### Life System
- Initial Lives: 3
- Life Loss Triggers:
  * Collision with alien projectiles
  * Collision with regular aliens
  * Mystery aliens reaching bottom screen
- Game Over Conditions:
  * Lives reach 0
  * Regular aliens reach bottom
- Visual/Audio Feedback:
  * Explosion animation on life loss
  * Different sounds for hit/game over
  * Score saving on game over

### Game Constants
- `MAX_SHOTS`: Maximum player bullets (2)
- `ALIEN_ODDS`: Alien spawn probability (22)
- `BOMB_ODDS`: Bomb drop probability (60)
- `ALIEN_RELOAD`: Frames between alien spawns (12)
- `SCREENRECT`: Game window dimensions (640x480)

## Technical Features

### Sprite Management
- Uses Pygame's sprite groups for efficient rendering
- Implements dirty rectangle optimization
- Manages sprite lifecycles through kill() method

### Collision Detection
- Sprite-based collision detection using sprite groups
- Hitbox adjustments for accurate collisions
- Collision response through explosion animations

### Animation System
- Frame-based animation for aliens
- State-based animation for explosions
- Smooth player movement animations

### Sound System
```python
class SoundManager:
    - Manages all game audio including sound effects and music
    - Properties:
        * sounds: Dictionary of loaded sound effects
        * volume_levels: Default volumes for different sound categories
        * music_channel: Dedicated channel for background music
    - Methods:
        * play(): Play a sound with category-specific volume
        * set_volume(): Adjust volume for specific sound category
        * get_volume(): Get current volume for a sound category
        * pause_music()/unpause_music(): Control background music
```

#### Volume Levels
- Background music: 50%
- Player shooting: 40%
- Explosions: 60%
- Shield/Health effects: 50%
- Boss-related sounds: 70%
- Warning/Level completion: 60-70%

### Background System
```python
class ParallaxBackground:
    - Manages multi-layered scrolling background
    - Properties:
        * layer_configs: Configuration for each background layer
        * backgrounds: List of loaded background images
        * layer_positions: Current scroll positions
    - Methods:
        * randomize_backgrounds(): Generate new random backgrounds
        * update(): Update scroll positions
        * draw(): Render all background layers
        * fade_transition(): Apply fade effect for transitions
```

#### Background Layers
1. Front Layer (Purple Nebula)
   - Fastest scroll speed (2.0)
   - Most visible parallax effect
2. Middle Layer (Green Nebula)
   - Medium scroll speed (0.5)
   - Moderate parallax effect
3. Back Layer (Blue Nebula)
   - Slowest scroll speed (0.2)
   - Subtle parallax effect

Each layer randomly selects from 8 different nebula patterns when:
- Game starts
- Level changes
- Background randomization is triggered

### Level Transition System
```python
def changer_niveau():
    - Increments level counter
    - Randomizes background layers
    - Resets game entities:
        * Clears projectiles
        * Removes explosions
        * Resets powerups
    - Creates new wave of aliens
    - Repositions player
```

### Performance Optimizations
- Dirty rectangle rendering
- Sprite group management
- Efficient collision detection
- Resource preloading

## Game States
```python
class GameState:
    - NORMAL: Regular gameplay
    - BOSS_WARNING: Pre-boss warning phase
    - BOSS_TRANSITION: Transition to boss fight
    - BOSS_FIGHT: Active boss battle
```

## Configuration System
```python
# Window Settings
- LARGEUR: 1600 (Window width)
- HAUTEUR: 1200 (Window height)
- HUD_HAUTEUR: 60 (HUD height)

# Gameplay Parameters
- VITESSE_ALIEN: Base alien movement speed
- VITESSE_ALIEN_POST_BOSS: Increased speed after boss (1.5x)
- VITESSE_DESCENTE: Vertical movement speed
- FREQUENCE_TIR_ALIEN_BASE: Base alien shooting frequency
```

## Boss System
```python
class BossConstants:
    - Health System:
        * Base HP: 50
        * Level scaling: 15% per level
        * Max health: 1000
        * Damage resistance: 85%
    
    - Movement:
        * Base speed: 2
        * Vertical bounds: 100-300
        * Pattern duration: 5000ms
        * Pattern cooldown: 1000ms
    
    - Combat:
        * Phase thresholds: 70%, 30%
        * Shot cooldown: 1000ms
        * Burst size: 5 projectiles
        * Summon cooldown: 15000ms
    
    - Special Abilities:
        * Dash cooldown: 3000ms
        * Teleport cooldown: 4000ms
        * Flash duration: 200ms
```

## Asset Management
- Images loaded and converted for optimal performance
- Sound files loaded conditionally based on mixer availability
- Asset path management through main_dir variable

## Game Loop Implementation
1. Event Processing
   - Input handling
   - Window management
   - Quit conditions

2. State Updates
   - Sprite movement
   - Collision detection
   - Score updates
   - Animation updates

3. Rendering
   - Background drawing
   - Sprite rendering
   - Score display
   - Screen updates

## Dependencies
- Python 3.x
- Pygame library
- Standard library modules:
  * os
  * random
  * typing

### Menu System
```python
class MenuManager:
    - Manages all game menus and UI overlays
    - Components:
        * Pause Menu:
            - "P : CONTINUE" option
            - "ESC : QUIT" option
        * Game Over Menu:
            - "R : RESTART" option
            - "ESC : QUIT" option
            - Best score display with glow effect
    - Features:
        * Pulsating text effects
        * Score display with glow effects
        * Smooth transitions
        * Responsive layout
```

### Boss System

#### Boss Class
```python
class Boss(pygame.sprite.Sprite):
    - Properties:
        * health: Base health (150) with level scaling (30% per level)
        * damage_resistance: Takes 50% of incoming damage
        * speed: Base speed (2) with level scaling (20% per level, max 8)
        * phase: Current boss phase (1-3)
        * is_dead: Tracks boss's death state
        * vulnerable: Controls damage invulnerability
    - Methods:
        * update(): Handles pattern updates and movement
        * prendre_degats(): Applies damage with resistance
        * deplacer(): Updates position based on velocity
        * tirer(): Manages boss projectile creation
```

#### Boss Patterns
```python
class BossPattern:
    - Base class for all boss movement patterns
    - Properties:
        * duration: Pattern duration (3000ms)
        * is_finished: Pattern completion state
    - Methods:
        * start(): Initialize pattern timing
        * update(): Update pattern progress and position
        * get_position(): Get current boss position

class SineWavePattern(BossPattern):
    - Smooth sine wave movement pattern
    - Properties:
        * amplitude: 120% of boss's base amplitude
        * velocity: [speed * 1.5 * direction, wave_motion]
    - Behavior:
        * Horizontal movement with direction changes at boundaries
        * Vertical sine wave motion for smooth up/down movement

class Figure8Pattern(BossPattern):
    - Figure-8 movement pattern
    - Properties:
        * width: 35% of screen width
        * height: 60% of available height
    - Behavior:
        * Smooth lemniscate (figure-8) motion
        * Centered in boss's movement area

class SpiralPattern(BossPattern):
    - Spiral movement pattern
    - Properties:
        * duration: 4000ms (longer than base)
        * radius: Decreasing spiral radius
    - Behavior:
        * Outward to inward spiral motion
        * Flattened vertical scale (60%)
```

#### Boss Phases
1. Phase 1 (100%-70% health)
   - Simple patterns (SineWave)
   - Basic projectile patterns
   - Normal movement speed

2. Phase 2 (70%-30% health)
   - More complex patterns (SineWave, Figure8)
   - Increased projectile frequency
   - Faster movement speed

3. Phase 3 (30%-0% health)
   - All patterns available
   - Maximum projectile frequency
   - Rage mode activated
   - Fastest movement speed

#### Sound Effects
- Boss damage: 85% volume
- Boss rage: 70% volume
- Boss defeated: 70% volume
- Boss warning: 60% volume
- Phase change: 70% volume

### Pattern System
```python
class PatternManager:
    - Manages boss movement patterns
    - Properties:
        * available_patterns: Dictionary of patterns per phase
        * current_pattern: Active pattern instance
        * pattern_cooldown: Time between pattern changes
    - Methods:
        * select_new_pattern(): Choose and initialize new pattern
        * update_pattern(): Update current pattern state
```

#### Pattern Transitions
- 500ms cooldown between patterns
- Smooth velocity-based movement
- Boundary enforcement with bounce effect
- Pattern-specific timing and durations
