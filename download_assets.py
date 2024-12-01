import os
import urllib.request
import zipfile
import shutil

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, filename):
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

# Create directories
base_dir = os.path.dirname(os.path.abspath(__file__))
effects_dir = os.path.join(base_dir, "assets", "images", "effects")
sounds_dir = os.path.join(base_dir, "assets", "sounds")

ensure_dir(effects_dir)
ensure_dir(sounds_dir)

# Download image assets
image_urls = {
    "space_effects.zip": "https://opengameart.org/sites/default/files/SpaceEffectsPack.zip",
    "particles.png": "https://opengameart.org/sites/default/files/particles_0.png",
    "effects.zip": "https://opengameart.org/sites/default/files/effects.zip"
}

# Download sound assets
sound_urls = {
    "warning.mp3": "https://freesound.org/data/previews/243/243020_3255160-lq.mp3",
    "teleport.mp3": "https://freesound.org/data/previews/220/220173_1442525-lq.mp3",
    "phase_change.mp3": "https://freesound.org/data/previews/220/220162_1442525-lq.mp3",
    "damage.mp3": "https://freesound.org/data/previews/220/220163_1442525-lq.mp3"
}

# Download and process images
for filename, url in image_urls.items():
    output_path = os.path.join(effects_dir, filename)
    download_file(url, output_path)
    
    # Extract if it's a zip file
    if filename.endswith('.zip'):
        try:
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                zip_ref.extractall(effects_dir)
            os.remove(output_path)  # Remove zip after extraction
            print(f"Extracted {filename}")
        except Exception as e:
            print(f"Error extracting {filename}: {e}")

# Download sounds
for filename, url in sound_urls.items():
    output_path = os.path.join(sounds_dir, filename)
    download_file(url, output_path)

print("\nAsset download complete!")
print("\nNext steps:")
print("1. Convert the .mp3 files to .wav format using an audio converter")
print("2. Rename the files to match the expected filenames in the code")
print("3. Review and organize the extracted image assets")
