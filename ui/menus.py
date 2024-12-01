import pygame
import math
import random
from config import LARGEUR, HAUTEUR, BLANC, VERT, ROUGE, NOIR
import os

class MenuState:
    def __init__(self):
        self.boss_pos = [LARGEUR // 2, HAUTEUR // 3]
        self.boss_target = [LARGEUR // 2, HAUTEUR // 3]
        self.boss_speed = 2
        self.boss_last_target_change = 0
        self.selected_ship_index = 0
        self.ships = []
        self.ship_names = []
        self.last_key_time = 0
        self.KEY_DELAY = 200
        self.font_cache = {}
        self.surface_cache = {}
        
    def get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]
    
    def load_resources(self):
        self.ships, self.ship_names = load_player_ships()

menu_state = MenuState()

def load_player_ships():
    """Load all player ship images from the assets/images/player directory."""
    ships = []
    ship_names = []
    player_dir = os.path.join('assets', 'images', 'player')
    
    if not os.path.exists(player_dir):
        print(f"Warning: Player directory not found: {player_dir}")
        return ships, ship_names
        
    try:
        for filename in os.listdir(player_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    image_path = os.path.join(player_dir, filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    scaled_size = (80, 80)
                    image = pygame.transform.smoothscale(image, scaled_size)
                    ships.append(image)
                    ship_names.append(os.path.splitext(filename)[0])
                except pygame.error as e:
                    print(f"Error loading ship image {filename}: {e}")
                except Exception as e:
                    print(f"Unexpected error loading {filename}: {e}")
    except Exception as e:
        print(f"Error accessing player directory: {e}")
        
    return ships, ship_names

def load_alien_images():
    """Load alien images for the menu display."""
    # Create default colored rectangles as fallback
    alien_images = []
    for i in range(3):
        surface = pygame.Surface((40, 40))
        surface.fill((0, 255, 0))  # Green color
        alien_images.append(surface)
    
    try:
        # Try to import and use the asset loader
        from utils.assets_loader import load_alien_images as load_aliens
        loaded_images = load_aliens()
        if loaded_images:
            alien_images = loaded_images
    except ImportError:
        pass  # Use fallback images if import fails
    
    return alien_images

def get_selected_ship():
    """Get the currently selected ship image."""
    if menu_state.ships and menu_state.selected_ship_index >= 0 and menu_state.selected_ship_index < len(menu_state.ships):
        print(f"Returning selected ship {menu_state.selected_ship_index}")
        return menu_state.ships[menu_state.selected_ship_index]
    print("No ship selected or invalid selection")
    return None

def create_particle_effect(surface, pos, color, size, alpha):
    particle_surface = surface.get_rect().copy()
    particle_surface.fill((0, 0, 0, 0))
    pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
    return particle_surface

def create_glow_effect(surface, color, alpha, size):
    glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*color, alpha), (size//2, size//2), size//2)
    return glow_surface

def handle_ship_selection_input(temps):
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()
    
    if current_time - menu_state.last_key_time > menu_state.KEY_DELAY:  # Only process key if enough time has passed
        if keys[pygame.K_LEFT] and menu_state.selected_ship_index > 0:
            menu_state.selected_ship_index -= 1
            menu_state.last_key_time = current_time
        elif keys[pygame.K_RIGHT] and menu_state.selected_ship_index < len(menu_state.ships) - 1:
            menu_state.selected_ship_index += 1
            menu_state.last_key_time = current_time

def draw_background_effects(fenetre, temps):
    # Enhanced background with multiple particle systems
    fenetre.fill(NOIR)
    
    # Create particle systems
    # 1. Background stars (small, twinkling)
    for layer in range(3):
        speed = (layer + 1) * 10
        size_range = (1, 2 + layer)
        count = 30 + layer * 20
        for i in range(count):
            x = (temps // speed + i * 40) % LARGEUR
            y = (i * 30 + temps // (speed * 2)) % HAUTEUR
            taille = random.randint(*size_range)
            luminosite = int(abs(math.sin(temps/1000 + i + layer)) * 255)
            if layer == 0:
                color = (luminosite, luminosite, luminosite)
            elif layer == 1:
                color = (int(luminosite * 0.5), luminosite, luminosite)
            else:
                color = (luminosite, int(luminosite * 0.5), luminosite)
            pygame.draw.circle(fenetre, color, (x, y), taille)
    
    # 2. Energy particles (flowing up)
    num_energy_particles = 20
    for i in range(num_energy_particles):
        time_offset = (temps + i * 1000) / 2000
        x = LARGEUR // 2 + math.cos(time_offset) * 300
        y = (HAUTEUR + 50 - (temps + i * 200) % (HAUTEUR + 100))
        size = 2 + math.sin(time_offset) * 1
        alpha = max(0, min(255, int(255 * (1 - abs(y - HAUTEUR/2)/(HAUTEUR/2)))))
        particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (0, 255, 0, alpha), (int(size), int(size)), int(size))
        fenetre.blit(particle_surface, (x - size, y - size))
    
    # 3. Floating particles around menu items
    for i in range(15):
        time_offset = temps / 1000 + i * 0.5
        radius = 150 + math.sin(time_offset * 2) * 20
        angle = time_offset + i * (2 * math.pi / 15)
        x = LARGEUR // 2 + math.cos(angle) * radius
        y = HAUTEUR * 3/4 + math.sin(angle) * (radius * 0.3)
        size = 1 + abs(math.sin(time_offset * 3)) * 2
        alpha = max(0, min(255, int(128 + 127 * math.sin(time_offset * 2))))
        particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (0, 255, 0, alpha), (int(size), int(size)), int(size))
        fenetre.blit(particle_surface, (x - size, y - size))
    
    # 4. Title particle effects
    num_title_particles = 30
    title_y = HAUTEUR // 4
    for i in range(num_title_particles):
        time_offset = (temps + i * 200) / 1000
        spread = 300 + math.sin(time_offset) * 50
        x = LARGEUR // 2 + math.cos(time_offset + i) * spread
        y = title_y + math.sin(time_offset * 2 + i) * 20
        size = 1 + abs(math.sin(time_offset * 3)) * 1.5
        alpha = max(0, min(255, int(200 * (1 - abs(y - title_y)/100))))
        particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        r = max(0, min(255, int(128 + 127 * math.sin(time_offset))))
        g = max(0, min(255, int(200 + 55 * math.sin(time_offset * 1.5))))
        b = max(0, min(255, int(50 + 50 * math.sin(time_offset * 2))))
        pygame.draw.circle(particle_surface, (r, g, b, alpha), (int(size), int(size)), int(size))
        fenetre.blit(particle_surface, (x - size, y - size))
    
    # 5. Hover effect particles
    mouse_x, mouse_y = pygame.mouse.get_pos()
    num_hover_particles = 10
    hover_radius = 30
    for i in range(num_hover_particles):
        angle = (temps / 500 + i * (2 * math.pi / num_hover_particles))
        x = mouse_x + math.cos(angle) * hover_radius
        y = mouse_y + math.sin(angle) * hover_radius
        size = 1 + abs(math.sin(temps/500 + i)) * 1.5
        alpha = max(0, min(255, int(100 + 50 * math.sin(temps/500 + i))))
        particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (0, 255, 255, alpha), (int(size), int(size)), int(size))
        fenetre.blit(particle_surface, (x - size, y - size))

def draw_menu_items(fenetre, temps):
    # Get window dimensions
    LARGEUR = fenetre.get_width()
    HAUTEUR = fenetre.get_height()
    
    # Calculate menu dimensions and position
    menu_width = 400
    menu_height = 500
    menu_x = (LARGEUR - menu_width) // 2
    menu_y = (HAUTEUR - menu_height) // 2
    
    temps = pygame.time.get_ticks()
    
    # Get alien images with enhanced positioning
    alien_images = load_alien_images()
    total_width = len(alien_images) * 160
    start_x = (LARGEUR - total_width) // 2 + 80
    
    # Draw aliens with enhanced effects and particles
    for i, img in enumerate(alien_images):
        x = start_x + i * 160
        base_y = HAUTEUR//2 + 50  # Moved lower (added 50 pixels)
        y = base_y + math.sin(temps/500 + i) * 20
        
        # Add shadow effect
        shadow_surface = img.copy()
        shadow_surface.fill((20, 20, 20, 128), special_flags=pygame.BLEND_RGBA_MULT)
        fenetre.blit(shadow_surface, (x - img.get_width()//2 + 5, y - img.get_height()//2 + 5))
        
        # Add glow effect
        glow_intensity = abs(math.sin(temps/1000 + i)) * 0.5 + 0.5
        glow_surface = img.copy()
        glow_surface.fill((int(128 * glow_intensity), int(255 * glow_intensity), int(128 * glow_intensity)), 
                         special_flags=pygame.BLEND_RGB_ADD)
        fenetre.blit(glow_surface, (x - img.get_width()//2, y - img.get_height()//2))
        
        # Add particle trail effect for aliens
        num_trail_particles = 5
        for j in range(num_trail_particles):
            time_offset = (temps + j * 200) / 1000
            trail_x = x + math.sin(time_offset * 2) * 10
            trail_y = y + 20 + j * 4
            size = 2 * (1 - j/num_trail_particles)
            alpha = max(0, min(255, int(200 * (1 - j/num_trail_particles))))
            particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (0, 255, 0, alpha), (int(size), int(size)), int(size))
            fenetre.blit(particle_surface, (trail_x - size, trail_y - size))
        
        # Draw the actual alien
        fenetre.blit(img, (x - img.get_width()//2, y - img.get_height()//2))
    
    # Update boss position
    if temps - menu_state.boss_last_target_change > 3000:  # Change target every 3 seconds
        menu_state.boss_target = [random.randint(100, LARGEUR-100), random.randint(100, HAUTEUR//2)]
        menu_state.boss_last_target_change = temps
    
    # Move boss towards target with smooth easing
    dx = menu_state.boss_target[0] - menu_state.boss_pos[0]
    dy = menu_state.boss_target[1] - menu_state.boss_pos[1]
    distance = math.sqrt(dx*dx + dy*dy)
    if distance > 0:
        menu_state.boss_pos[0] += (dx/distance) * menu_state.boss_speed
        menu_state.boss_pos[1] += (dy/distance) * menu_state.boss_speed
    
    # Add slight hovering effect
    hover_offset = math.sin(temps/500) * 10
    
    # Draw the boss with effects
    boss_images = load_alien_images()  # Get the boss images
    if boss_images:
        current_boss = boss_images[len(boss_images)-1]  # Use the last image (usually the biggest/boss)
        # Scale up the boss image
        scale_factor = 1.5  # Increase size by 50%
        scaled_size = (int(current_boss.get_width() * scale_factor), 
                      int(current_boss.get_height() * scale_factor))
        current_boss = pygame.transform.smoothscale(current_boss, scaled_size)
        boss_rect = current_boss.get_rect()
        
        # Add shadow effect (scaled up)
        shadow_surface = pygame.Surface(current_boss.get_size(), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))
        fenetre.blit(shadow_surface, (menu_state.boss_pos[0] - boss_rect.width//2 + 15, 
                                    menu_state.boss_pos[1] - boss_rect.height//2 + hover_offset + 15))
        
        # Add glow effect (scaled up)
        glow_size = max(boss_rect.width, boss_rect.height) + 40
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_alpha = int(128 * (0.7 + math.sin(temps/500) * 0.3))
        pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), 
                         (glow_size//2, glow_size//2), glow_size//2)
        fenetre.blit(glow_surface, (menu_state.boss_pos[0] - glow_size//2,
                                   menu_state.boss_pos[1] - glow_size//2 + hover_offset))
        
        # Draw the boss
        fenetre.blit(current_boss, (menu_state.boss_pos[0] - boss_rect.width//2,
                                   menu_state.boss_pos[1] - boss_rect.height//2 + hover_offset))
        
        # Add particle trail effect (scaled up)
        for i in range(5):
            particle_alpha = int(200 * (1 - i/5))
            particle_size = int(15 * (1 - i/5))  # Increased base particle size
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (255, 0, 0, particle_alpha),
                             (particle_size, particle_size), particle_size)
            offset = i * 8  # Increased spacing between particles
            fenetre.blit(particle_surface, (menu_state.boss_pos[0] - particle_size + math.sin(temps/200 + i) * 8,
                                          menu_state.boss_pos[1] - particle_size + hover_offset + offset))
    
    # Menu items with enhanced effects
    font_instructions = menu_state.get_font(36)
    instructions = [
        ("PRESS SPACE TO START", menu_y + 20, None, (0, 255, 0)),
        ("MOVE", menu_y + 85, None, (0, 255, 255)),
        ("SPACE : SHOOT", menu_y + 150, None, (255, 255, 0)),
        ("P : PAUSE", menu_y + 195, None, (255, 128, 0)),
        ("ESC : QUIT", menu_y + 240, None, (255, 0, 0))
    ]
    
    # Draw instructions with enhanced effects
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for i, (texte, y, _, base_color) in enumerate(instructions):
        hover = y - 10 <= mouse_y <= y + 30 and menu_x <= mouse_x <= menu_x + menu_width
        
        if texte == "MOVE":
            # Calculate center positions
            center_x = LARGEUR // 2
            text_y = y
            
            # Render MOVE text first to get its width
            move_text = font_instructions.render(texte, True, base_color)
            text_width = move_text.get_width()
            
            # Calculate total width including arrows and spacing
            arrow_spacing = 20
            total_width = text_width + (arrow_spacing * 2)
            
            # Calculate starting x position to center everything
            start_x = center_x - (total_width // 2)
            
            # Draw arrows with enhanced pulsing effect
            arrow_pulse = abs(math.sin(temps/500)) * 0.3 + 0.7
            arrow_color = (0, int(255*arrow_pulse), int(255*arrow_pulse))
            
            # Left and right arrows
            left_arrow = font_instructions.render("<<", True, arrow_color)
            right_arrow = font_instructions.render(">>", True, arrow_color)
            left_x = start_x - left_arrow.get_width() - 5
            right_x = start_x + total_width + 5
            
            # Add glow effect for arrows when hovering
            if hover:
                glow_size = int(20 * (1 + math.sin(temps/300) * 0.3))
                glow_alpha = int(128 * (0.7 + math.sin(temps/300) * 0.3))
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*arrow_color, glow_alpha), (glow_size, glow_size), glow_size)
                fenetre.blit(glow_surface, (left_x - glow_size//2, text_y - glow_size//2))
                fenetre.blit(glow_surface, (right_x - glow_size//2, text_y - glow_size//2))
            
            fenetre.blit(left_arrow, (left_x, text_y))
            fenetre.blit(right_arrow, (right_x, text_y))
            
            # Draw the MOVE text with glow effect when hovering
            if hover:
                glow_text = font_instructions.render(texte, True, (0, 255, 255))
                glow_surface = pygame.Surface((text_width + 20, 40), pygame.SRCALPHA)
                glow_alpha = int(100 * (0.7 + math.sin(temps/300) * 0.3))
                glow_surface.fill((0, 255, 255, glow_alpha))
                fenetre.blit(glow_surface, (center_x - text_width//2 - 10, text_y - 5))
            
            text_x = center_x - (text_width // 2)
            fenetre.blit(move_text, (text_x, text_y))
            
        else:
            # Enhanced regular instruction rendering
            pulse = 1.0 if not hover else abs(math.sin(temps/500)) * 0.3 + 0.7
            color = tuple(int(c * pulse) for c in base_color)
            instruction = font_instructions.render(texte, True, color)
            rect_instruction = instruction.get_rect(center=(LARGEUR // 2, y))
            
            # Add glow effect when hovering
            if hover:
                glow_surface = pygame.Surface((instruction.get_width() + 20, 40), pygame.SRCALPHA)
                glow_alpha = int(100 * (0.7 + math.sin(temps/300) * 0.3))
                glow_surface.fill((*base_color, glow_alpha))
                fenetre.blit(glow_surface, (rect_instruction.x - 10, rect_instruction.y - 5))
            
            fenetre.blit(instruction, rect_instruction)
        
        # Add hover line effect
        if hover:
            line_width = menu_width - 40 if texte != "MOVE" else total_width + left_arrow.get_width() + right_arrow.get_width() + 40
            line_x = LARGEUR//2 - line_width//2
            line_alpha = int(abs(math.sin(temps/300)) * 255)
            line_surface = pygame.Surface((line_width, 2), pygame.SRCALPHA)
            line_surface.fill((*base_color, line_alpha))
            fenetre.blit(line_surface, (line_x, y + (30 if texte == "MOVE" else instruction.get_height() + 5)))

def draw_ship_selection(fenetre, temps):
    # Draw section title with enhanced design
    font_title = menu_state.get_font(48)  # Larger font size
    selection_text = "SELECT YOUR SHIP"
    
    # Create the main text surface
    text_surface = font_title.render(selection_text, True, (0, 255, 255))  # Cyan color
    text_rect = text_surface.get_rect(center=(LARGEUR // 2, HAUTEUR - 200))
    
    # Create metallic panel background
    panel_padding = 20
    panel_rect = text_rect.inflate(panel_padding * 2, panel_padding * 2)
    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    
    # Draw metallic background with gradient
    base_color = (30, 30, 40, 200)
    highlight_color = (50, 50, 60, 200)
    pygame.draw.rect(panel_surface, base_color, panel_surface.get_rect(), border_radius=10)
    
    # Add highlight effect
    highlight_rect = pygame.Rect(2, 2, panel_rect.width-4, panel_rect.height//2)
    pygame.draw.rect(panel_surface, highlight_color, highlight_rect, border_radius=10)
    
    # Add animated border glow
    pulse = abs(math.sin(temps/1000)) * 0.5 + 0.5
    glow_alpha = int(100 * pulse)
    pygame.draw.rect(panel_surface, (0, 255, 255, glow_alpha), panel_surface.get_rect(), 
                    width=2, border_radius=10)
    
    # Position and draw the panel
    panel_rect.center = text_rect.center
    fenetre.blit(panel_surface, panel_rect)
    
    # Create scanline effect
    scanline_offset = (temps // 50) % panel_rect.height
    scanline_alpha = int(20 + 10 * math.sin(temps/200))
    scanline = pygame.Surface((panel_rect.width, 2), pygame.SRCALPHA)
    scanline.fill((255, 255, 255, scanline_alpha))
    for y in range(0, panel_rect.height, 4):
        pos_y = (y + scanline_offset) % panel_rect.height
        if pos_y < panel_rect.height:
            fenetre.blit(scanline, (panel_rect.left, panel_rect.top + pos_y))
    
    # Draw text with multi-layer effect
    offset = 2
    colors = [(0, 150, 255), (0, 200, 255), (0, 255, 255)]  # Blue to cyan gradient
    
    for i, color in enumerate(colors):
        offset_y = math.sin(temps/300 + i) * 2
        layer_surface = font_title.render(selection_text, True, color)
        pos = (text_rect.centerx - layer_surface.get_width()//2 + math.sin(temps/400 + i) * offset,
               text_rect.centery - layer_surface.get_height()//2 + offset_y)
        fenetre.blit(layer_surface, pos)
    
    # Add chromatic aberration effect
    red_surface = font_title.render(selection_text, True, (255, 0, 0))
    blue_surface = font_title.render(selection_text, True, (0, 0, 255))
    aberration_offset = math.sin(temps/500) * 2
    
    fenetre.blit(red_surface, (text_rect.centerx - red_surface.get_width()//2 - aberration_offset,
                              text_rect.centery - red_surface.get_height()//2), special_flags=pygame.BLEND_ADD)
    fenetre.blit(blue_surface, (text_rect.centerx - blue_surface.get_width()//2 + aberration_offset,
                               text_rect.centery - blue_surface.get_height()//2), special_flags=pygame.BLEND_ADD)
    
    # Calculate positions for ship display
    ship_spacing = 120  # Increased spacing for larger ships
    total_width = len(menu_state.ships) * ship_spacing
    start_x = (LARGEUR - total_width) // 2 + ship_spacing // 2
    
    # Draw ships
    for i, ship in enumerate(menu_state.ships):
        x = start_x + i * ship_spacing
        y = HAUTEUR - 100  
        ship_rect = ship.get_rect(center=(x, y))
        
        # Draw selection highlight
        if i == menu_state.selected_ship_index:
            # Draw glow effect
            glow_size = 90  
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            glow_alpha = int(128 * (0.7 + math.sin(temps/300) * 0.3))
            pygame.draw.circle(glow_surface, (0, 255, 255, glow_alpha), 
                             (glow_size//2, glow_size//2), glow_size//2)
            fenetre.blit(glow_surface, (x - glow_size//2, y - glow_size//2))
        
        # Draw ship
        fenetre.blit(ship, ship_rect)
        
        # Add hover effect for selected ship
        if i == menu_state.selected_ship_index:
            hover_offset = math.sin(temps/300) * 5
            ship_rect.y += hover_offset
            fenetre.blit(ship, ship_rect)
    
    # Draw selection arrows
    arrow_y = HAUTEUR - 100  
    arrow_font = menu_state.get_font(48)
    
    # Left arrow
    if menu_state.selected_ship_index > 0:
        left_arrow = arrow_font.render("<<", True, (0, 255, 255))
        left_x = start_x - ship_spacing//2 - left_arrow.get_width()
        fenetre.blit(left_arrow, (left_x, arrow_y))
        
        # Add glow effect
        glow_alpha = int(128 * (0.7 + math.sin(temps/300) * 0.3))
        glow_surface = pygame.Surface(left_arrow.get_size(), pygame.SRCALPHA)
        glow_surface.fill((0, 255, 255, glow_alpha))
        fenetre.blit(glow_surface, (left_x, arrow_y))
    
    # Right arrow
    if menu_state.selected_ship_index < len(menu_state.ships) - 1:
        right_arrow = arrow_font.render(">>", True, (0, 255, 255))
        right_x = start_x + (len(menu_state.ships) - 1) * ship_spacing + ship_spacing//2
        fenetre.blit(right_arrow, (right_x, arrow_y))
        
        # Add glow effect
        glow_alpha = int(128 * (0.7 + math.sin(temps/300) * 0.3))
        glow_surface = pygame.Surface(right_arrow.get_size(), pygame.SRCALPHA)
        glow_surface.fill((0, 255, 255, glow_alpha))
        fenetre.blit(glow_surface, (right_x, arrow_y))

def update_boss_movement(temps):
    if temps - menu_state.boss_last_target_change > 3000:  # Change target every 3 seconds
        menu_state.boss_target = [random.randint(100, LARGEUR-100), random.randint(100, HAUTEUR//2)]
        menu_state.boss_last_target_change = temps
    
    # Move boss towards target with smooth easing
    dx = menu_state.boss_target[0] - menu_state.boss_pos[0]
    dy = menu_state.boss_target[1] - menu_state.boss_pos[1]
    distance = math.sqrt(dx*dx + dy*dy)
    if distance > 0:
        menu_state.boss_pos[0] += (dx/distance) * menu_state.boss_speed
        menu_state.boss_pos[1] += (dy/distance) * menu_state.boss_speed

def draw_boss(fenetre, temps):
    # Add slight hovering effect
    hover_offset = math.sin(temps/500) * 10
    
    # Draw the boss with effects
    boss_images = load_alien_images()  # Get the boss images
    if boss_images:
        current_boss = boss_images[len(boss_images)-1]  # Use the last image (usually the biggest/boss)
        # Scale up the boss image
        scale_factor = 1.5  # Increase size by 50%
        scaled_size = (int(current_boss.get_width() * scale_factor), 
                      int(current_boss.get_height() * scale_factor))
        current_boss = pygame.transform.smoothscale(current_boss, scaled_size)
        boss_rect = current_boss.get_rect()
        
        # Add shadow effect (scaled up)
        shadow_surface = pygame.Surface(current_boss.get_size(), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))
        fenetre.blit(shadow_surface, (menu_state.boss_pos[0] - boss_rect.width//2 + 15, 
                                    menu_state.boss_pos[1] - boss_rect.height//2 + hover_offset + 15))
        
        # Add glow effect (scaled up)
        glow_size = max(boss_rect.width, boss_rect.height) + 40
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_alpha = int(128 * (0.7 + math.sin(temps/500) * 0.3))
        pygame.draw.circle(glow_surface, (255, 0, 0, glow_alpha), 
                         (glow_size//2, glow_size//2), glow_size//2)
        fenetre.blit(glow_surface, (menu_state.boss_pos[0] - glow_size//2,
                                   menu_state.boss_pos[1] - glow_size//2 + hover_offset))
        
        # Draw the boss
        fenetre.blit(current_boss, (menu_state.boss_pos[0] - boss_rect.width//2,
                                   menu_state.boss_pos[1] - boss_rect.height//2 + hover_offset))
        
        # Add particle trail effect (scaled up)
        for i in range(5):
            particle_alpha = int(200 * (1 - i/5))
            particle_size = int(15 * (1 - i/5))  # Increased base particle size
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (255, 0, 0, particle_alpha),
                             (particle_size, particle_size), particle_size)
            offset = i * 8  # Increased spacing between particles
            fenetre.blit(particle_surface, (menu_state.boss_pos[0] - particle_size + math.sin(temps/200 + i) * 8,
                                          menu_state.boss_pos[1] - particle_size + hover_offset + offset))

def draw_title_and_score(fenetre, temps, meilleur_score):
    """Draw the animated WindSurf INVADERS title and high score."""
    # Title setup
    font_titre = menu_state.get_font(100)
    texte_base = 'WINDSURF INVADERS'
    
    # Calculate title position - moved higher (from HAUTEUR//4 to HAUTEUR//6)
    title_y = HAUTEUR//6
    
    # Title background glow
    glow_width = 600
    glow_height = 120
    glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
    for i in range(glow_height):
        alpha = int(20 * (1 - abs(i - glow_height/2)/(glow_height/2)))
        pygame.draw.line(glow_surface, (0, 255, 0, alpha), (0, i), (glow_width, i))
    fenetre.blit(glow_surface, (LARGEUR//2 - glow_width//2, title_y - glow_height//2))
    
    # Multiple layers for enhanced glitch effect
    for i in range(3):
        offset = int(math.sin(temps/300 + i) * 4)
        glitch_x = random.randint(-2, 2) if temps % 200 < 50 else 0
        glitch_y = random.randint(-2, 2) if temps % 200 < 50 else 0
        
        # Random corruption effect
        if temps % 500 < 50 and i == 0:
            corrupt_chars = list(texte_base)
            corrupt_pos = random.randint(0, len(corrupt_chars)-1)
            corrupt_chars[corrupt_pos] = chr(random.randint(33, 90))
            texte_base = "".join(corrupt_chars)
        
        couleurs = [(255, 0, 0), (0, 255, 0), (0, 200, 0)]
        titre = font_titre.render(texte_base, True, couleurs[i])
        pos_x = LARGEUR//2 - titre.get_width()//2 + offset + glitch_x
        pos_y = title_y + offset + glitch_y
        
        fenetre.blit(titre, (pos_x, pos_y))
    
    # High Score Display in top right corner
    pulse = abs(math.sin(temps/1000)) * 0.5 + 0.5
    padding = 20  # Padding from the screen edges
    
    # Score value with retro style
    font_score = menu_state.get_font(32)
    score_label = "HIGH SCORE"
    score_value = f"{meilleur_score:,}"
    
    # Render label and value separately for better styling
    label_surface = font_score.render(score_label, True, (255, 255, 0))  # Yellow color
    value_surface = font_score.render(score_value, True, (0, 255, 0))    # Green color
    
    # Calculate positions
    panel_padding = 15
    value_rect = value_surface.get_rect()
    label_rect = label_surface.get_rect()
    
    # Align text: label on top, value below
    total_height = label_rect.height + value_rect.height + 5  # 5px spacing between texts
    panel_rect = pygame.Rect(0, 0, 
                           max(label_rect.width, value_rect.width) + panel_padding * 2,
                           total_height + panel_padding * 2)
    panel_rect.topright = (LARGEUR - padding, padding)
    
    # Score background panel with metallic effect
    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    base_color = (30, 30, 40, 200)
    highlight_color = (50, 50, 60, 200)
    
    # Draw main panel background
    pygame.draw.rect(panel_surface, base_color, panel_surface.get_rect(), border_radius=8)
    
    # Add metallic highlight effect
    highlight_rect = pygame.Rect(2, 2, panel_rect.width-4, panel_rect.height//2)
    pygame.draw.rect(panel_surface, highlight_color, highlight_rect, border_radius=8)
    
    # Add border glow
    glow_alpha = int(100 * pulse)
    pygame.draw.rect(panel_surface, (0, 255, 0, glow_alpha), panel_surface.get_rect(), 
                    width=2, border_radius=8)
    
    # Position the panel
    fenetre.blit(panel_surface, panel_rect)
    
    # Position and draw the text with glow
    label_pos = (panel_rect.centerx - label_rect.width//2, 
                panel_rect.y + panel_padding)
    value_pos = (panel_rect.centerx - value_rect.width//2,
                label_pos[1] + label_rect.height + 5)
    
    # Draw text glow
    glow_alpha = int(128 * pulse)
    for surface, pos, color in [(label_surface, label_pos, (255, 255, 0)),
                               (value_surface, value_pos, (0, 255, 0))]:
        glow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        glow_surface.fill((*color, glow_alpha))
        fenetre.blit(glow_surface, pos)
        fenetre.blit(surface, pos)

def dessiner_menu_accueil(fenetre, meilleur_score):
    """Draw the main menu with all visual effects."""
    temps = pygame.time.get_ticks()
    
    # Handle input
    handle_ship_selection_input(temps)
    
    # Draw background
    draw_background_effects(fenetre, temps)
    
    # Draw title and score
    draw_title_and_score(fenetre, temps, meilleur_score)
    
    # Draw menu elements
    draw_menu_items(fenetre, temps)
    
    # Draw ship selection
    draw_ship_selection(fenetre, temps)
    
    # Update boss movement
    update_boss_movement(temps)
    
    # Draw boss
    draw_boss(fenetre, temps)

def dessiner_menu_pause(fenetre):
    temps = pygame.time.get_ticks()
    
    # Create scanline effect
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    
    # Add scanlines
    for y in range(0, HAUTEUR, 2):
        pygame.draw.line(overlay, (0, 20, 0, 50), (0, y), (LARGEUR, y))
    
    fenetre.blit(overlay, (0, 0))
    
    # Pause text with glitch effect
    font_titre = pygame.font.Font(None, 74)
    texte_base = "PAUSE"
    
    # Multiple layers for glitch effect
    for i in range(3):
        offset = int(math.sin(temps/300 + i) * 4)
        glitch_x = random.randint(-2, 2) if temps % 200 < 50 else 0
        glitch_y = random.randint(-2, 2) if temps % 200 < 50 else 0
        
        couleurs = [(255, 0, 0), (0, 255, 0), (0, 200, 0)]
        titre = font_titre.render(texte_base, True, couleurs[i])
        rect_titre = titre.get_rect(
            center=(LARGEUR // 2 + offset + glitch_x, 
                   HAUTEUR // 3 + offset + glitch_y)
        )
        fenetre.blit(titre, rect_titre)
    
    # Instructions with pulsating effect
    font_instructions = pygame.font.Font(None, 36)
    instructions = [
        'P pour reprendre',
        'ESC pour quitter'
    ]
    
    for i, texte in enumerate(instructions):
        pulse = abs(math.sin(temps/1000 + i/2)) * 0.3 + 0.7
        instruction = font_instructions.render(texte, True, (0, int(255*pulse), 0))
        rect_instruction = instruction.get_rect(
            center=(LARGEUR // 2, HAUTEUR // 2 + i * 50)
        )
        fenetre.blit(instruction, rect_instruction)

def dessiner_game_over(fenetre, score, meilleur_score):
    temps = pygame.time.get_ticks()
    
    # Create a temporary surface for wave effect
    temp_surface = fenetre.copy()
    surface_go = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    
    # Wave effect
    for y in range(0, HAUTEUR, 4):
        offset = int(math.sin(temps/1000 + y/100) * 10)
        rect_source = pygame.Rect(0, y, LARGEUR, 2)
        surface_go.blit(temp_surface, (offset, y), rect_source)
    
    # Scanlines with green tint
    for y in range(0, HAUTEUR, 2):
        pygame.draw.line(surface_go, (0, 20, 0, 50), (0, y), (LARGEUR, y))
    
    # Dark overlay with green tint
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.fill((0, 20, 0))
    overlay.set_alpha(220)
    surface_go.blit(overlay, (0, 0))
    
    fenetre.blit(surface_go, (0, 0))
    
    # Game Over text with glitch effect
    font_go = pygame.font.Font(None, 120)
    texte_base = "GAME OVER"
    
    # Multi-layer effect for "GAME OVER"
    for i in range(3):
        offset = int(math.sin(temps/300 + i) * 4)
        glitch_x = random.randint(-2, 2) if temps % 200 < 50 else 0
        glitch_y = random.randint(-2, 2) if temps % 200 < 50 else 0
        
        # Random corruption effect
        if temps % 500 < 50 and i == 0:
            corrupt_chars = list(texte_base)
            corrupt_pos = random.randint(0, len(corrupt_chars)-1)
            corrupt_chars[corrupt_pos] = chr(random.randint(33, 90))
            texte_corrompu = "".join(corrupt_chars)
            texte_go = font_go.render(texte_corrompu, True, (255, 0, 0))
        else:
            texte_go = font_go.render(texte_base, True, (255, 0, 0))
        
        pos_x = LARGEUR//2 - texte_go.get_width()//2 + offset + glitch_x
        pos_y = HAUTEUR//3 + offset + glitch_y
        
        fenetre.blit(texte_go, (pos_x, pos_y))
    
    # Score display with pulsating effect
    font_score = pygame.font.Font(None, 60)
    pulse = abs(math.sin(temps/1000)) * 0.2 + 0.8
    
    # Current score
    score_formatte = f"{score:,}"
    texte_score = font_score.render(f"SCORE: {score_formatte}", True, (0, int(255*pulse), 0))
    pos_score = (LARGEUR//2 - texte_score.get_width()//2, HAUTEUR//2)
    
    # High score with glow effect
    meilleur_formatte = f"{meilleur_score:,}"
    texte_meilleur = font_score.render(f"MEILLEUR SCORE: {meilleur_formatte}", True, (0, 255, 0))
    pos_meilleur = (LARGEUR//2 - texte_meilleur.get_width()//2, HAUTEUR//2 + 70)
    
    # Add "halo" effect around scores
    for surface, pos in [(texte_score, pos_score), (texte_meilleur, pos_meilleur)]:
        for i in range(3):
            offset = i * 2
            alpha = int(255 * (1 - i/3) * pulse)
            halo_surface = surface.copy()
            halo_surface.set_alpha(alpha)
            fenetre.blit(halo_surface, (pos[0]-offset, pos[1]-offset))
        fenetre.blit(surface, pos)
    
    # Instructions with flashing effect
    font_instructions = pygame.font.Font(None, 40)
    alpha = int(abs(math.sin(temps/500)) * 255)
    
    instructions = [
        ("R pour recommencer", HAUTEUR//2 + 160),
        ("ESC pour quitter", HAUTEUR//2 + 200)
    ]
    
    for texte, y in instructions:
        instruction_surface = font_instructions.render(texte, True, (0, 255, 0))
        instruction_surface.set_alpha(alpha)
        pos_x = LARGEUR//2 - instruction_surface.get_width()//2
        fenetre.blit(instruction_surface, (pos_x, y))
        
        # Pulsating horizontal line
        ligne_longueur = instruction_surface.get_width() + 40
        ligne_x = LARGEUR//2 - ligne_longueur//2
        pygame.draw.line(fenetre, (0, int(100*pulse), 0),
                        (ligne_x, y + 30),
                        (ligne_x + ligne_longueur, y + 30), 1)

menu_state.load_resources()
