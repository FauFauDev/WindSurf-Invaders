import pygame
import math
from config import LARGEUR, HAUTEUR, HUD_HAUTEUR, BLANC, VERT, ROUGE, VIES_MAX

def dessiner_hud(fenetre, score, vies, niveau, meilleur_score, joueur):
    temps = pygame.time.get_ticks()
    
    # Draw background
    pygame.draw.rect(fenetre, (20, 20, 20), (0, 0, LARGEUR, HUD_HAUTEUR))
    
    # Draw score with pulsating effect
    font = pygame.font.Font(None, 36)
    pulse = abs(math.sin(temps/1000)) * 0.2 + 0.8
    score_formatte = f"{score:,}"
    score_text = font.render(f'Score: {score_formatte}', True, (0, int(255*pulse), 0))
    fenetre.blit(score_text, (10, 10))
    
    # Draw high score with neon effect
    high_score_formatte = f"{meilleur_score:,}"
    for i in range(3):
        alpha = int(255 * (1 - i/3) * pulse)
        high_score_surface = font.render(f'Meilleur Score: {high_score_formatte}', True, (0, 255, 0))
        high_score_surface.set_alpha(alpha)
        offset = i * 2
        fenetre.blit(high_score_surface, 
                    (LARGEUR - high_score_surface.get_width() - 10 - offset, 
                     10 - offset))
    
    # Draw level with glowing effect
    niveau_text = font.render(f'Niveau: {niveau}', True, (0, int(255*pulse), 0))
    niveau_pos = (LARGEUR // 2 - niveau_text.get_width() // 2, 10)
    for i in range(2):
        glow_surface = niveau_text.copy()
        glow_surface.set_alpha(128 * (1-i))
        fenetre.blit(glow_surface, (niveau_pos[0]-i, niveau_pos[1]-i))
    fenetre.blit(niveau_text, niveau_pos)
    
    # Draw lives with animated icons
    dessiner_vies(fenetre, vies, temps)
    
    # Draw energy bar with dynamic effects
    dessiner_barre_energie(fenetre, joueur, temps)

def dessiner_vies(fenetre, vies, temps):
    font = pygame.font.Font(None, 36)
    vies_text = font.render(f'Vies:', True, BLANC)
    fenetre.blit(vies_text, (200, 10))
    
    # Draw animated life icons
    for i in range(min(vies, VIES_MAX)):
        pulse = abs(math.sin(temps/1000 + i/2)) * 0.3 + 0.7
        couleur = (0, int(255*pulse), 0)
        pygame.draw.circle(fenetre, couleur, (280 + i * 20, 20), 8)
        pygame.draw.circle(fenetre, (0, int(100*pulse), 0), (280 + i * 20, 20), 6)

def dessiner_barre_energie(fenetre, joueur, temps):
    # Draw energy bar background with gradient
    for i in range(200):
        couleur = (int(50 + i/4), 0, 0)
        pygame.draw.line(fenetre, couleur, (400 + i, 15), (400 + i, 35))
    
    # Draw current energy level with pulse effect
    energie_width = (joueur.energie / 100) * 200
    pulse = abs(math.sin(temps/500)) * 0.2 + 0.8
    for i in range(int(energie_width)):
        intensity = int(255 * pulse * (0.7 + 0.3 * (i/200)))
        couleur = (0, intensity, 0)
        pygame.draw.line(fenetre, couleur, (400 + i, 15), (400 + i, 35))
    
    # Draw energy text with glow
    font = pygame.font.Font(None, 24)
    energie_text = font.render(f'Energie: {int(joueur.energie)}%', True, BLANC)
    text_pos = (450, 17)
    
    # Add glow effect
    for i in range(2):
        glow_surface = energie_text.copy()
        glow_surface.set_alpha(128 * (1-i))
        fenetre.blit(glow_surface, (text_pos[0]-i, text_pos[1]-i))
    fenetre.blit(energie_text, text_pos)

def dessiner_barre_vie(fenetre, joueur, x, y, vies):
    temps = pygame.time.get_ticks()
    largeur_barre = 50
    hauteur_barre = 5
    
    # Draw health bar with dynamic effects
    if joueur.est_invincible:
        pulse = abs(math.sin(temps/200)) * 0.3 + 0.7
        couleur = (int(255*pulse), int(215*pulse), 0)
    elif joueur.shield_actif:
        pulse = abs(math.sin(temps/300)) * 0.3 + 0.7
        couleur = (0, int(191*pulse), int(255*pulse))
    else:
        pulse = abs(math.sin(temps/1000)) * 0.2 + 0.8
        couleur = (0, int(255*pulse), 0)
    
    # Draw bar with gradient
    for i in range(largeur_barre):
        intensity = int(couleur[1] * (0.7 + 0.3 * (i/largeur_barre)))
        current_color = (couleur[0], intensity, couleur[2])
        pygame.draw.line(fenetre, current_color, (x + i, y), (x + i, y + hauteur_barre))
    
    # Draw lives indicator with pulsating effect
    for i in range(min(vies, VIES_MAX)):
        pulse = abs(math.sin(temps/1000 + i/2)) * 0.3 + 0.7
        couleur = (0, int(255*pulse), 0)
        pygame.draw.circle(fenetre, couleur, (x + 10 + i * 15, y - 10), 5)
        pygame.draw.circle(fenetre, (0, int(100*pulse), 0), (x + 10 + i * 15, y - 10), 3)
