# Space Invaders Game Overview

## Game Description
Space Invaders is a classic arcade-style shooter game implemented in Python using the Pygame library. The game puts players in control of a spaceship defending against waves of alien invaders.

## Game Mechanics

### Player Controls
- **Movement**: Left and right arrow keys to move the player's spaceship horizontally
- **Shooting**: Space bar to fire bullets at the aliens
- **Display**: F key to toggle fullscreen mode

### Core Game Elements

#### Core Mechanics
- Player moves horizontally at bottom of screen
- Shoot projectiles upward to destroy aliens
- Dodge alien projectiles
- Collect power-ups for special abilities

#### Lives System
- Player starts with 3 lives
- Lives are lost when:
  * Hit by alien projectiles
  * Hit by regular aliens
  * Mystery aliens reach the bottom of the screen
- Game ends when all lives are lost

#### Enemy Types
1. Regular Aliens
   - Move in one of three formations:
     * Triangle: Growing rows (3 to 7 aliens per row)
     * Circle: Double ring formation (inner and outer circles)
     * Wave: 3 rows of 6 aliens in wave pattern
   - Formation-specific shooting patterns
   - Points vary based on position and formation
   - Increased difficulty after boss fights

2. Formation Behaviors
   - Triangle Formation:
     * Front row shoots more frequently
     * Each row wider than the previous
     * Higher rows worth more points
   - Circle Formation:
     * Inner circle (8 aliens) and outer circle (12 aliens)
     * Outer circle aliens shoot more frequently
     * Continuous orbital movement
   - Wave Formation:
     * Synchronized wave-like movement
     * Increased shooting at wave peaks/troughs
     * Side-to-side movement while maintaining pattern

3. Mystery Aliens
   - Appear randomly in waves of 1-3
   - Follow unique movement patterns (wave, zigzag, circular)
   - Fire targeted projectiles at player
   - Worth high points when destroyed
   - Cause life loss if they reach the bottom
   - Rotate while moving for visual effect

4. Boss Aliens
   - Appear every few levels
   - Have multiple attack patterns
   - Require multiple hits to destroy
   - Drop power-ups when defeated

### Game Features
- Score tracking system
- Sound effects and background music with balanced volume levels
- Dynamic background system with random nebula patterns per level
- Fullscreen toggle capability
- Animated explosions
- Sprite-based graphics
- Parallax scrolling backgrounds with three layers:
  * Front layer (Purple Nebula, fast scroll)
  * Middle layer (Green Nebula, medium scroll)
  * Back layer (Blue Nebula, slow scroll)

## Game Flow
1. Game initializes with player at bottom of screen
2. Aliens spawn at regular intervals
3. Player moves and shoots to destroy aliens
4. Aliens move horizontally and drop bombs
5. Score increases as aliens are destroyed
6. Upon level completion:
   - Background changes to new random nebula patterns
   - New wave of aliens spawns
   - Difficulty increases
7. Game continues until player is hit by alien or bomb

## Technical Implementation
The game uses Pygame's sprite system for efficient collision detection and rendering. It employs dirty rectangle optimization for improved performance and includes a comprehensive sound system with both sound effects and background music. Sound levels are carefully balanced for optimal gaming experience:
- Background music plays at moderate volume (50%)
- Frequent sounds like shooting are kept lower (40%)
- Important events like explosions and boss appearances are more prominent (60-70%)
- Warning sounds and level completion effects are clearly audible (60-70%)
