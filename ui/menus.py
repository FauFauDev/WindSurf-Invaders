import pygame
import math
import random
from config import LARGEUR, HAUTEUR, BLANC, VERT, ROUGE, NOIR
import os

from utils.control_settings import ControlSettings

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
        self.star_positions = []
        self.orbit_phase = 0.0
        self.active_view = 'main'
        self.controls_selection = 0
        self.awaiting_binding = None
        self.binding_feedback = ''
        self.binding_feedback_time = 0

    def get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]
    
    def load_resources(self):
        self.ships, self.ship_names = load_player_ships()
        self.ensure_starfield()
    def ensure_starfield(self):
        if self.star_positions:
            return
        for _ in range(140):
            self.star_positions.append({
                'x': random.randint(0, LARGEUR),
                'y': random.randint(0, HAUTEUR),
                'tone': random.random(),
                'speed': random.uniform(0.0012, 0.0025),
                'drift': random.uniform(0.02, 0.06),
            })


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
                    image = pygame.image.load(image_path)
                    if pygame.display.get_surface():
                        image = image.convert_alpha()
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
    if menu_state.active_view != 'main' or menu_state.awaiting_binding:
        return

    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()
    
    if current_time - menu_state.last_key_time > menu_state.KEY_DELAY:  # Only process key if enough time has passed
        if keys[pygame.K_LEFT] and menu_state.selected_ship_index > 0:
            menu_state.selected_ship_index -= 1
            menu_state.last_key_time = current_time
        elif keys[pygame.K_RIGHT] and menu_state.selected_ship_index < len(menu_state.ships) - 1:
            menu_state.selected_ship_index += 1
            menu_state.last_key_time = current_time


def handle_menu_event(event, controls):
    if event.type != pygame.KEYDOWN:
        return None

    action_labels = dict(ControlSettings.ACTIONS)

    if menu_state.active_view == 'controls':
        if menu_state.awaiting_binding:
            if event.key == pygame.K_ESCAPE:
                menu_state.awaiting_binding = None
                menu_state.binding_feedback = 'Binding cancelled'
                menu_state.binding_feedback_time = pygame.time.get_ticks()
                return 'handled'

            action = menu_state.awaiting_binding
            controls.set_binding(action, event.key)
            key_name = ControlSettings.format_key(event.key)
            label = action_labels.get(action, action.title())
            menu_state.binding_feedback = f"{label} bound to {key_name}"
            menu_state.binding_feedback_time = pygame.time.get_ticks()
            menu_state.awaiting_binding = None
            return 'handled'

        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            menu_state.active_view = 'main'
            menu_state.awaiting_binding = None
            menu_state.binding_feedback = ''
            return 'handled'

        if event.key in (pygame.K_DOWN, pygame.K_s):
            menu_state.controls_selection = (menu_state.controls_selection + 1) % len(ControlSettings.ACTIONS)
            menu_state.binding_feedback = ''
            return 'handled'

        if event.key in (pygame.K_UP, pygame.K_w):
            menu_state.controls_selection = (menu_state.controls_selection - 1) % len(ControlSettings.ACTIONS)
            menu_state.binding_feedback = ''
            return 'handled'

        if event.key in (pygame.K_RETURN, controls.get('fire')):
            action, label = ControlSettings.ACTIONS[menu_state.controls_selection]
            menu_state.awaiting_binding = action
            menu_state.binding_feedback = f"Press new key for {label}"
            menu_state.binding_feedback_time = pygame.time.get_ticks()
            return 'handled'

        if event.key == pygame.K_r:
            controls.reset_defaults()
            menu_state.binding_feedback = 'Controls reset to defaults'
            menu_state.binding_feedback_time = pygame.time.get_ticks()
            return 'handled'

        return None

    if event.key in (controls.get('fire'), pygame.K_RETURN):
        return 'start'

    if event.key == pygame.K_c:
        menu_state.active_view = 'controls'
        menu_state.controls_selection = 0
        menu_state.awaiting_binding = None
        menu_state.binding_feedback = ''
        menu_state.binding_feedback_time = pygame.time.get_ticks()
        return 'handled'

    if event.key == pygame.K_ESCAPE:
        return 'quit'

    return None



def draw_background_effects(fenetre, temps):
    menu_state.ensure_starfield()
    fenetre.fill((0, 0, 0))

    vignette = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    centre = pygame.math.Vector2(LARGEUR / 2, HAUTEUR / 2 + 40)
    for radius in range(260, 520, 40):
        alpha = max(0, 80 - (radius - 260) * 0.5)
        if alpha <= 0:
            continue
        pygame.draw.circle(vignette, (12, 26, 54, int(alpha)), centre, radius, width=0)
    fenetre.blit(vignette, (0, 0), special_flags=pygame.BLEND_ADD)

    grid_surface = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    for column in range(0, LARGEUR, 140):
        alpha = 18 + int(12 * math.sin(temps / 900 + column * 0.01))
        pygame.draw.line(grid_surface, (40, 80, 120, alpha), (column, 0), (column, HAUTEUR))
    for row in range(0, HAUTEUR, 120):
        alpha = 12 + int(10 * math.cos(temps / 700 + row * 0.02))
        pygame.draw.line(grid_surface, (30, 60, 90, alpha), (0, row), (LARGEUR, row))
    fenetre.blit(grid_surface, (0, 0))

    for star in menu_state.star_positions:
        drift_y = (star['y'] + temps * star['drift']) % HAUTEUR
        twinkle = 0.55 + 0.45 * math.sin(temps * star['speed'] + star['tone'] * math.pi * 2)
        colour_scale = 90 + int(80 * star['tone'])
        colour = (
            int(colour_scale * 0.3),
            int(colour_scale * 0.6 * twinkle),
            int(colour_scale * twinkle),
        )
        pygame.draw.circle(fenetre, colour, (int(star['x']), int(drift_y)), 1, width=0)
        if twinkle > 0.9:
            pygame.draw.circle(fenetre, colour, (int(star['x']), int(drift_y)), 2, width=1)

    wave_surface = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    base_y = HAUTEUR / 2 + 50
    for band in range(3):
        path_points = []
        amplitude = 18 + band * 8
        wavelength = 220 + band * 40
        for x in range(-40, LARGEUR + 40, 12):
            phase = (temps / (650 - band * 60)) + (x / wavelength)
            y = base_y + math.sin(phase * math.pi * 2) * amplitude
            path_points.append((x, y))
        colour = (int(40 + band * 25), int(90 + band * 35), int(140 + band * 45))
        pygame.draw.lines(wave_surface, colour, False, path_points, 2)
    wave_surface.set_alpha(70)
    fenetre.blit(wave_surface, (0, 0), special_flags=pygame.BLEND_ADD)

def draw_menu_items(fenetre, temps, controls, show_instructions=True):
    LARGEUR = fenetre.get_width()
    HAUTEUR = fenetre.get_height()

    panel_width = 520
    panel_height = 420 if show_instructions else 260
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
    panel_rect.center = (LARGEUR // 2, HAUTEUR // 2 + 90)

    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel_surface.fill((15, 24, 45, 215))

    for y in range(24, panel_height, 36):
        alpha = 18 + int(10 * math.sin(temps / 400 + y * 0.05))
        pygame.draw.line(panel_surface, (70, 110, 185, alpha), (24, y), (panel_width - 24, y))

    highlight_primary = int((temps * 0.08) % panel_height)
    pygame.draw.rect(panel_surface, (60, 140, 255, 36), (0, highlight_primary, panel_width, 10))
    pygame.draw.rect(panel_surface, (40, 120, 220, 22), (0, (highlight_primary + panel_height // 2) % panel_height, panel_width, 8))
    pygame.draw.rect(panel_surface, (0, 170, 255, 110), panel_surface.get_rect(), width=2, border_radius=18)

    fenetre.blit(panel_surface, panel_rect.topleft)

    corner_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    for corner in ((18, 18), (panel_width - 18, 18), (18, panel_height - 18), (panel_width - 18, panel_height - 18)):
        pygame.draw.circle(corner_surface, (0, 150, 255, 70), corner, 20)
    fenetre.blit(corner_surface, panel_rect.topleft, special_flags=pygame.BLEND_ADD)

    if show_instructions:
        main_font = menu_state.get_font(34)
        detail_font = menu_state.get_font(24)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        fire_label = controls.key_label('fire') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['fire'])
        move_left = controls.key_label('move_left') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['move_left'])
        move_right = controls.key_label('move_right') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['move_right'])
        move_up = controls.key_label('move_up') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['move_up'])
        move_down = controls.key_label('move_down') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['move_down'])
        move_display = f"{move_left} / {move_right} / {move_up} / {move_down}"

        entries = [
            (f"PRESS {fire_label} TO START", (0, 220, 255)),
            ("MOVE", (0, 200, 240)),
            (f"{fire_label} : SHOOT", (255, 230, 120)),
            ("P : PAUSE", (255, 180, 90)),
            ("F : TOGGLE FULL SCREEN", (140, 220, 255)),
            ("C : CUSTOMIZE CONTROLS", (150, 200, 255)),
            ("ESC : QUIT", (255, 110, 120)),
        ]

        base_y = panel_rect.top + 100
        spacing = 56

        for idx, (text_label, colour) in enumerate(entries):
            line_rect = pygame.Rect(0, 0, panel_width - 80, 44)
            line_rect.center = (panel_rect.centerx, base_y + idx * spacing)
            hover = line_rect.collidepoint(mouse_x, mouse_y)

            if hover:
                highlight = pygame.Surface(line_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(highlight, (*colour, 40), highlight.get_rect(), border_radius=14)
                fenetre.blit(highlight, line_rect.topleft)

            accent_colour = tuple(min(255, int(c)) for c in colour)
            if text_label == 'MOVE':
                label_surface = main_font.render('MOVE', True, accent_colour)
                label_rect = label_surface.get_rect(center=(line_rect.centerx, line_rect.centery - 10))
                fenetre.blit(label_surface, label_rect)

                detail_surface = detail_font.render(move_display, True, (180, 210, 255))
                detail_rect = detail_surface.get_rect(center=(line_rect.centerx, line_rect.centery + 18))
                fenetre.blit(detail_surface, detail_rect)
            else:
                text_surface = main_font.render(text_label, True, accent_colour)
                text_rect = text_surface.get_rect(center=line_rect.center)
                fenetre.blit(text_surface, text_rect)

            left_node = (line_rect.centerx - panel_rect.width // 2 + 24, line_rect.centery)
            right_node = (line_rect.centerx + panel_rect.width // 2 - 24, line_rect.centery)
            pygame.draw.circle(fenetre, accent_colour, left_node, 3)
            pygame.draw.circle(fenetre, accent_colour, right_node, 3)

    for offset in range(4):
        angle = temps / 900 + offset * (math.pi / 2)
        node_x = panel_rect.centerx + math.cos(angle) * (panel_rect.width / 2 + 30)
        node_y = panel_rect.centery + math.sin(angle) * (panel_rect.height / 2 + 12)
        pygame.draw.circle(fenetre, (80, 170, 255), (int(node_x), int(node_y)), 4)

def draw_controls_menu(fenetre, temps, controls):
    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((10, 20, 40, 180))
    fenetre.blit(overlay, (0, 0))

    panel_width = 760
    panel_height = 520
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
    panel_rect.center = (LARGEUR // 2, HAUTEUR // 2)

    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel_surface.fill((20, 30, 50, 235))
    pygame.draw.rect(panel_surface, (0, 255, 200, 120), panel_surface.get_rect(), width=2, border_radius=12)

    title_font = menu_state.get_font(56)
    row_font = menu_state.get_font(34)
    hint_font = menu_state.get_font(24)

    title = title_font.render("CONTROL SETUP", True, (0, 255, 200))
    title_glow = pygame.Surface(title.get_size(), pygame.SRCALPHA)
    title_glow.fill((0, 255, 200, 60))
    title_pos = (panel_rect.width // 2 - title.get_width() // 2, 40)
    panel_surface.blit(title_glow, title_pos)
    panel_surface.blit(title, title_pos)

    bindings = list(controls.iter_bindings()) if controls else [(action, label, ControlSettings.DEFAULT_BINDINGS[action]) for action, label in ControlSettings.ACTIONS]

    key_usage = {}
    for _, _, key in bindings:
        key_usage[key] = key_usage.get(key, 0) + 1

    has_duplicates = any(count > 1 for count in key_usage.values())

    row_start = 120
    row_height = 56
    row_spacing = 14

    for idx, (action, label, key) in enumerate(bindings):
        row_rect = pygame.Rect(30, row_start + idx * (row_height + row_spacing), panel_width - 60, row_height)
        is_selected = idx == menu_state.controls_selection
        is_waiting = menu_state.awaiting_binding == action
        base_color = (30, 45, 70, 160)
        highlight_color = (60, 110, 160, 210)
        waiting_color = (0, 160, 200, 220)
        color = waiting_color if is_waiting else highlight_color if is_selected else base_color
        pygame.draw.rect(panel_surface, color, row_rect, border_radius=10)
        border_color = (0, 255, 200, 160) if is_selected else (0, 120, 200, 110)
        pygame.draw.rect(panel_surface, border_color, row_rect, width=2, border_radius=10)

        if is_selected and not is_waiting:
            pointer = row_font.render(">>", True, (0, 255, 200))
            panel_surface.blit(pointer, (row_rect.x - 25, row_rect.y + (row_height - pointer.get_height()) // 2))

        label_surface = row_font.render(label.upper(), True, (200, 255, 255))
        panel_surface.blit(label_surface, (row_rect.x + 20, row_rect.y + (row_height - label_surface.get_height()) // 2))

        if is_waiting:
            key_text = "Press a key"
            key_color = (0, 255, 200)
        else:
            key_text = ControlSettings.format_key(key)
            key_color = (255, 255, 255)
            if key_usage.get(key, 0) > 1:
                key_color = (255, 140, 0)

        key_surface = row_font.render(key_text.upper(), True, key_color)
        panel_surface.blit(key_surface, (row_rect.right - key_surface.get_width() - 20, row_rect.y + (row_height - key_surface.get_height()) // 2))

    hint_y = panel_height - 120
    fire_label = controls.key_label('fire') if controls else ControlSettings.format_key(ControlSettings.DEFAULT_BINDINGS['fire'])
    hints = [
        f"ENTER / {fire_label}: REBIND",
        "R: RESET DEFAULTS",
        "ESC / BACKSPACE: BACK"
    ]

    if has_duplicates:
        hints.append("ORANGE KEYS NEED ATTENTION")

    for offset, text in enumerate(hints):
        hint_surface = hint_font.render(text, True, (160, 210, 255))
        panel_surface.blit(hint_surface, (panel_rect.width // 2 - hint_surface.get_width() // 2, hint_y + offset * 24))

    if menu_state.binding_feedback:
        elapsed = pygame.time.get_ticks() - menu_state.binding_feedback_time
        if elapsed < 2200:
            alpha = max(60, 255 - int((elapsed / 2200) * 180))
            feedback_surface = hint_font.render(menu_state.binding_feedback.upper(), True, (0, 255, 200))
            feedback_surface.set_alpha(alpha)
            panel_surface.blit(feedback_surface, (panel_rect.width // 2 - feedback_surface.get_width() // 2, hint_y - 40))

    fenetre.blit(panel_surface, panel_rect.topleft)


def draw_ship_selection(fenetre, temps):
    if not menu_state.ships:
        return

    centre_x = LARGEUR // 2
    base_y = HAUTEUR - 160

    title_font = menu_state.get_font(36)
    subtitle_font = menu_state.get_font(22)

    title_surface = title_font.render('Fleet Selection', True, (190, 220, 255))
    title_rect = title_surface.get_rect(center=(centre_x, base_y - 90))
    fenetre.blit(title_surface, title_rect)
    pygame.draw.line(fenetre, (70, 170, 255), (title_rect.left - 30, title_rect.bottom + 6), (title_rect.right + 30, title_rect.bottom + 6), 2)

    platform_surface = pygame.Surface((LARGEUR, 220), pygame.SRCALPHA)
    ellipse_rect = pygame.Rect(0, 0, 460, 120)
    ellipse_rect.center = (centre_x, base_y + 40)
    pygame.draw.ellipse(platform_surface, (30, 120, 255, 50), ellipse_rect)
    pygame.draw.ellipse(platform_surface, (90, 200, 255, 30), ellipse_rect.inflate(40, -18), 1)
    fenetre.blit(platform_surface, (0, HAUTEUR - 220), special_flags=pygame.BLEND_ADD)

    ship_spacing = 160
    ship_count = len(menu_state.ships)
    start_x = centre_x - ((ship_count - 1) * ship_spacing) // 2

    for idx, ship in enumerate(menu_state.ships):
        x = start_x + idx * ship_spacing
        is_selected = idx == menu_state.selected_ship_index

        ship_surface = ship.copy()
        if not is_selected:
            ship_surface.fill((150, 150, 150, 180), special_flags=pygame.BLEND_RGBA_MULT)

        offset = math.sin(temps / 320 + idx) * 6 if is_selected else 0
        ship_rect = ship_surface.get_rect(center=(x, base_y + offset))
        fenetre.blit(ship_surface, ship_rect)

        if is_selected:
            glow_surface = pygame.Surface((ship_rect.width + 60, ship_rect.height + 60), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (80, 200, 255, 120), (glow_surface.get_width() // 2, glow_surface.get_height() // 2), glow_surface.get_width() // 2)
            pygame.draw.circle(glow_surface, (120, 220, 255, 60), (glow_surface.get_width() // 2, glow_surface.get_height() // 2), glow_surface.get_width() // 2 - 10, width=3)
            fenetre.blit(glow_surface, (ship_rect.centerx - glow_surface.get_width() // 2, ship_rect.centery - glow_surface.get_height() // 2), special_flags=pygame.BLEND_ADD)

        name = menu_state.ship_names[idx] if idx < len(menu_state.ship_names) else f'Ship {idx + 1}'
        name_surface = subtitle_font.render(name.upper(), True, (200, 230, 255) if is_selected else (110, 140, 170))
        name_rect = name_surface.get_rect(center=(x, ship_rect.bottom + 28))
        fenetre.blit(name_surface, name_rect)

    arrow_colour = (120, 200, 255)
    arrow_size = 24
    if menu_state.selected_ship_index > 0:
        centre = (start_x - ship_spacing // 2, base_y)
        points = [
            (centre[0] + arrow_size // 2, centre[1]),
            (centre[0] - arrow_size // 2, centre[1] - arrow_size),
            (centre[0] - arrow_size // 2, centre[1] + arrow_size),
        ]
        pygame.draw.polygon(fenetre, arrow_colour, points)
    if menu_state.selected_ship_index < ship_count - 1:
        centre = (start_x + ship_spacing * (ship_count - 1) + ship_spacing // 2, base_y)
        points = [
            (centre[0] - arrow_size // 2, centre[1]),
            (centre[0] + arrow_size // 2, centre[1] - arrow_size),
            (centre[0] + arrow_size // 2, centre[1] + arrow_size),
        ]
        pygame.draw.polygon(fenetre, arrow_colour, points)

def update_boss_movement(temps):
    menu_state.orbit_phase = temps / 900.0


def draw_boss(fenetre, temps):
    centre = pygame.math.Vector2(LARGEUR / 2, HAUTEUR / 2 + 90)
    halo_surface = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    pygame.draw.circle(halo_surface, (30, 120, 255, 30), (int(centre.x), int(centre.y)), 200, width=0)
    pygame.draw.circle(halo_surface, (60, 180, 255, 45), (int(centre.x), int(centre.y)), 140, width=2)

    for idx in range(6):
        angle = menu_state.orbit_phase + idx * (math.pi / 3)
        radius = 180 + math.sin(temps / 650 + idx) * 18
        x = centre.x + math.cos(angle) * radius
        y = centre.y + math.sin(angle) * radius * 0.35
        size = 6 if idx % 2 == 0 else 4
        colour = (80 + idx * 25, 200, 255, 120)
        pygame.draw.circle(halo_surface, colour, (int(x), int(y)), size)

    fenetre.blit(halo_surface, (0, 0), special_flags=pygame.BLEND_ADD)

def draw_title_and_score(fenetre, temps, meilleur_score):
    """Draw the animated Nebula Surge title and high score."""
    # Title setup
    font_titre = menu_state.get_font(100)
    texte_base = 'Nebula Surge'
    
    # Calculate title position - moved higher (from HAUTEUR//4 to HAUTEUR//6)
    title_y = HAUTEUR//6
    
    # Title background glow
    glow_width = 600
    glow_height = 120
    glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
    for i in range(glow_height):
        alpha = int(20 * (1 - abs(i - glow_height/2)/(glow_height/2)))
        pygame.draw.line(glow_surface, (25, 110, 255, alpha), (0, i), (glow_width, i))
    fenetre.blit(glow_surface, (LARGEUR//2 - glow_width//2, title_y - glow_height//2))


    blue_palette = [
        (60, 150, 255),
        (100, 180, 255),
        (150, 210, 255),
    ]

    for i in range(3):
        offset = int(math.sin(temps / 300 + i) * 4)
        glitch_x = random.randint(-2, 2) if temps % 200 < 50 else 0
        glitch_y = random.randint(-2, 2) if temps % 200 < 50 else 0

        if temps % 500 < 50 and i == 0:
            corrupt_chars = list(texte_base)
            corrupt_pos = random.randint(0, len(corrupt_chars) - 1)
            corrupt_chars[corrupt_pos] = chr(random.randint(33, 90))
            text_variant = ''.join(corrupt_chars)
        else:
            text_variant = texte_base

        titre = font_titre.render(text_variant, True, blue_palette[i])
        pos_x = LARGEUR // 2 - titre.get_width() // 2 + offset + glitch_x
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

def dessiner_menu_accueil(fenetre, meilleur_score, controls):
    """Draw the main menu with all visual effects."""
    temps = pygame.time.get_ticks()

    if menu_state.active_view == 'main':
        handle_ship_selection_input(temps)

    draw_background_effects(fenetre, temps)
    draw_title_and_score(fenetre, temps, meilleur_score)

    draw_menu_items(fenetre, temps, controls, show_instructions=menu_state.active_view == 'main')

    if menu_state.active_view == 'main':
        draw_ship_selection(fenetre, temps)

    update_boss_movement(temps)
    draw_boss(fenetre, temps)

    if menu_state.active_view == 'controls':
        draw_controls_menu(fenetre, temps, controls)

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
        
        couleurs = [(110, 200, 255), (80, 160, 255), (60, 120, 220)]
        titre = font_titre.render(texte_base, True, couleurs[i])
        rect_titre = titre.get_rect(
            center=(LARGEUR // 2 + offset + glitch_x, 
                   HAUTEUR // 3 + offset + glitch_y)
        )
        fenetre.blit(titre, rect_titre)
    
    # Instructions with pulsating effect
    font_instructions = pygame.font.Font(None, 36)
    instructions = [
        'P : CONTINUE',
        'ESC : QUIT'
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
    texte_meilleur = font_score.render(f"BEST SCORE: {meilleur_formatte}", True, (0, 255, 0))
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
        ("R : RESTART", HAUTEUR//2 + 160),
        ("ESC : QUIT", HAUTEUR//2 + 200)
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
