import pygame
import random
import os
from config import ASSETS_DIR

class PowerUp:
    def __init__(self, x, y, type_powerup, image):
        self.type = type_powerup
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.vitesse = 2

    def deplacer(self):
        self.rect.y += self.vitesse
        return self.rect.top <= 1200  # Using HAUTEUR constant

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)

    def appliquer(self, joueur, vies):
        if self.type == "shield":
            joueur.shield_actif = True
            joueur.shield_temps = pygame.time.get_ticks()
            return vies
        elif self.type == "life" and vies < 3:  # Map 'vie' to 'life'
            return vies + 1
        elif self.type == "fire":  # Map 'tir_rapide' to 'fire'
            joueur.rapid_fire = True
            joueur.rapid_fire_timer = pygame.time.get_ticks()
            return vies
        return vies

def generer_power_up(x, y, images):
    """Generate a random power-up at the given position."""
    types = ["shield", "life", "fire"]  # Use the mapped types directly
    type_powerup = random.choice(types)
    return PowerUp(x, y, type_powerup, images['powerups'][type_powerup])
