import pygame
import math
import random
from config import VITESSE_PROJECTILE_ALIEN, LARGEUR

class Projectile:
    def __init__(self, x, y, image, type_tir='normal'):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x 
        self.rect.bottom = y
        self.vitesse = 7
        self.type_tir = type_tir
        self.trainee = []
        self.max_trainee = 4
        
        # Ajustement de la taille du rectangle de collision pour un meilleur gameplay
        self.rect.width = self.rect.width // 2
        self.rect.height = self.rect.height // 2
        
        # Set damage based on projectile type
        if type_tir == 'puissant':
            self.vitesse = 10
            self.damage = 2  # Powerful shots do 2 damage
            self.max_trainee = 4
        elif type_tir == 'rapide':
            self.vitesse = 12
            self.damage = 1  # Rapid shots do 1 damage
            self.max_trainee = 6
        else:  # normal shot
            self.damage = 1  # Normal shots do 1 damage

        self.a_touche = False

    def dessiner(self, fenetre):
        # Draw trail effect for rapid fire
        if self.type_tir == 'rapide':
            for i, pos in enumerate(self.trainee):
                alpha = int(255 * ((i + 1) / self.max_trainee) * 0.6)
                trail_surface = self.image.copy()
                trail_surface.set_alpha(alpha)
                trail_rect = trail_surface.get_rect(center=pos)
                fenetre.blit(trail_surface, trail_rect)

        if self.type_tir == 'puissant':
            # Draw glow effect for powerful shots
            glow_surface = pygame.Surface((self.rect.width + 4, self.rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 100, 100, 150), glow_surface.get_rect())
            fenetre.blit(glow_surface, self.rect.inflate(4, 4))
            pygame.draw.rect(fenetre, (255, 0, 0), self.rect)
        else:
            fenetre.blit(self.image, self.rect)

    def deplacer(self):
        if self.type_tir == 'rapide':
            self.trainee.append(self.rect.center)
            if len(self.trainee) > self.max_trainee:
                self.trainee.pop(0)
        self.rect.y -= self.vitesse

class ProjectileAlien:
    def __init__(self, x, y, image, type_alien, rangee):
        self.vitesse = VITESSE_PROJECTILE_ALIEN
        self.type_alien = type_alien
        self.image_originale = image
        self.image = self.image_originale
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.angle = 0
        self.trainee = []  # Stockera (position, angle)
        self.max_trainee = 6  # Augmenté pour une traînée plus longue
        
        if type_alien > 1:
            self.vitesse += type_alien * 0.5
            
        self.rotation_speed = random.randint(3, 8)

    def deplacer(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        
        # Ajout de la position actuelle à la traînée
        self.trainee.append((self.rect.center, self.angle))
        if len(self.trainee) > self.max_trainee:
            self.trainee.pop(0)
            
        self.rect.y += self.vitesse
        if self.type_alien > 2:
            self.rect.x += math.sin(self.rect.y / 30) * 2

    def dessiner(self, fenetre):
        # Dessin de la traînée avec opacité plus élevée
        for i, (pos, angle) in enumerate(self.trainee[:-1]):  # Exclure la dernière position
            alpha = int(255 * ((i + 1) / self.max_trainee) * 0.7)  # Augmenté à 0.7
            trainee_surface = pygame.transform.rotate(self.image_originale, angle)
            trainee_surface.set_alpha(alpha)
            trainee_rect = trainee_surface.get_rect(center=pos)
            fenetre.blit(trainee_surface, trainee_rect)
        
        # Dessin du projectile principal
        self.image = pygame.transform.rotate(self.image_originale, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        fenetre.blit(self.image, self.rect)

class ProjectileMystereAgressif:
    """Projectile spécial pour les aliens mystères qui suit le joueur"""
    def __init__(self, x, y, dx, dy, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.dx = dx
        self.dy = dy
        self.damage = 2  # More damage than regular projectiles
        
        # Rotate image based on direction
        angle = math.degrees(math.atan2(-dy, dx))  # Negative dy because pygame y increases downward
        self.image = pygame.transform.rotate(image, angle - 90)  # -90 to point in direction of movement
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Keep projectile within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.dx = -self.dx
        elif self.rect.right > LARGEUR:
            self.rect.right = LARGEUR
            self.dx = -self.dx

    def deplacer(self):
        """Alias for update to maintain consistency with other projectile classes"""
        self.update()

    def dessiner(self, fenetre):
        fenetre.blit(self.image, self.rect)

class ProjectileMystere:
    def __init__(self, x, y, dx, dy, image):
        self.image_originale = image
        self.image = self.image_originale
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.dx = dx
        self.dy = dy
        self.vitesse = math.sqrt(dx*dx + dy*dy)  # Calcul de la vitesse totale
        self.angle = 0
        self.trainee = []
        self.max_trainee = 8  # Traînée plus longue pour les projectiles mystère
        self.rotation_speed = random.randint(5, 12)

    def deplacer(self):
        self.angle = (self.angle + self.rotation_speed) % 360
        
        # Ajout de la position actuelle à la traînée
        self.trainee.append((self.rect.center, self.angle))
        if len(self.trainee) > self.max_trainee:
            self.trainee.pop(0)
            
        self.rect.x += self.dx
        self.rect.y += self.dy

    def dessiner(self, fenetre):
        # Dessin de la traîne avec effet de brillance plus visible
        for i, (pos, angle) in enumerate(self.trainee[:-1]):  # Exclure la dernière position
            alpha = int(255 * ((i + 1) / self.max_trainee) * 0.8)  # Augmenté à 0.8
            
            trainee_surface = pygame.transform.rotate(self.image_originale, angle)
            glow_surface = trainee_surface.copy()
            
            # Augmentation de l'opacité de la brillance
            glow_surface.set_alpha(alpha // 2)
            trainee_surface.set_alpha(alpha)
            
            trainee_rect = trainee_surface.get_rect(center=pos)
            glow_rect = glow_surface.get_rect(center=pos)
            
            # Brillance plus large
            fenetre.blit(glow_surface, glow_rect.inflate(8, 8))
            fenetre.blit(trainee_surface, trainee_rect)
        
        # Dessin du projectile principal avec brillance renforcée
        self.image = pygame.transform.rotate(self.image_originale, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        glow_surface = self.image.copy()
        glow_surface.set_alpha(150)  # Augmenté à 150
        glow_rect = glow_surface.get_rect(center=self.rect.center)
        
        fenetre.blit(glow_surface, glow_rect.inflate(8, 8))
        fenetre.blit(self.image, self.rect)
