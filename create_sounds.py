import wave
import struct
import math
import os

def create_sound(filename, frequency, duration, volume=0.5, sample_rate=44100):
    # Calculate the number of frames needed
    num_frames = int(duration * sample_rate)
    
    # Open the wave file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Generate frames
        for i in range(num_frames):
            t = float(i) / sample_rate
            # Basic sine wave
            value = math.sin(2.0 * math.pi * frequency * t)
            # Apply volume
            value = int(value * 32767.0 * volume)
            # Write frame
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def create_warning_sound():
    # Create a warning beep sound
    frequency = 440  # A4 note
    duration = 0.5   # Half second
    create_sound('assets/sounds/boss_warning.wav', frequency, duration)

def create_teleport_sound():
    # Create a sci-fi teleport sound (ascending frequency)
    with wave.open('assets/sounds/boss_teleport.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        
        for i in range(44100):  # 1 second
            t = float(i) / 44100
            # Frequency sweeps from 200Hz to 2000Hz
            frequency = 200 + 1800 * t
            value = math.sin(2.0 * math.pi * frequency * t)
            # Apply envelope
            envelope = 1.0 if t < 0.8 else (1.0 - (t - 0.8) * 5.0)
            value = int(value * 32767.0 * 0.5 * envelope)
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def create_phase_change_sound():
    # Create a dramatic phase change sound
    with wave.open('assets/sounds/boss_phase_change.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        
        for i in range(int(44100 * 1.5)):  # 1.5 seconds
            t = float(i) / 44100
            # Mix multiple frequencies
            value = (
                math.sin(2.0 * math.pi * 200 * t) * 0.5 +
                math.sin(2.0 * math.pi * 400 * t) * 0.3 +
                math.sin(2.0 * math.pi * 600 * t) * 0.2
            )
            # Apply envelope
            envelope = min(t * 4, 1.0) if t < 0.25 else max(0, 1.0 - (t - 0.25))
            value = int(value * 32767.0 * envelope)
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def create_damage_sound():
    # Create an impact sound
    with wave.open('assets/sounds/boss_damage.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        
        for i in range(int(44100 * 0.2)):  # 0.2 seconds
            t = float(i) / 44100
            # Mix noise with a low frequency
            noise = math.sin(t * 1000000) * 0.5  # Pseudo-random noise
            tone = math.sin(2.0 * math.pi * 100 * t) * 0.5
            value = noise + tone
            # Sharp attack, quick decay
            envelope = math.exp(-t * 20)
            value = int(value * 32767.0 * envelope)
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def main():
    # Create sounds directory if it doesn't exist
    if not os.path.exists('assets/sounds'):
        os.makedirs('assets/sounds')
    
    print("Creating sound effects...")
    create_warning_sound()
    create_teleport_sound()
    create_phase_change_sound()
    create_damage_sound()
    print("Sound effects created in assets/sounds/")

if __name__ == '__main__':
    main()
