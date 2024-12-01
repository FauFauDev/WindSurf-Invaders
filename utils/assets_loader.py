import pygame
import os

def load_alien_images():
    """Load and return alien images for the menu."""
    # Define paths relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_root, 'assets', 'images', 'aliens')
    
    # List of alien image filenames
    alien_files = ['Ship1.png', 'Ship2.png', 'Ship3.png', 'Ship4.png', 'Ship5.png', 'Ship6.png']  # Using the actual filenames
    alien_images = []
    
    # Load each alien image
    for alien_file in alien_files:
        try:
            img_path = os.path.join(assets_dir, alien_file)
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                # Scale the image to a larger size
                img = pygame.transform.scale(img, (80, 80))  # Doubled the size
                alien_images.append(img)
            else:
                print(f"Image not found: {img_path}")  # Debug info
        except pygame.error as e:
            print(f"Error loading {alien_file}: {e}")  # Debug info
            # If image loading fails, create a fallback colored rectangle
            surface = pygame.Surface((80, 80))
            surface.fill((0, 255, 0))  # Green color for fallback
            alien_images.append(surface)
    
    # If no images were loaded, create default colored rectangles
    if not alien_images:
        print("No alien images loaded, using fallback")  # Debug info
        for _ in range(3):
            surface = pygame.Surface((80, 80))
            surface.fill((0, 255, 0))  # Green color
            alien_images.append(surface)
    
    return alien_images
