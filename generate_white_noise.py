import numpy as np
from scipy.io import wavfile
import os

# Parameters
sample_rate = 44100  # Hz (standard audio sampling rate)
duration = 60.0      # seconds (1 minute, suitable for looping in a video)
output_audio_file = "white_noise.wav"
amplitude = 0.1      # Reduced from 0.98 to 30% for lower volume
apply_compressor = False  # Disable compressor to avoid boosting loudness (optional)

# Step 1: Generate white noise
def generate_white_noise(sample_rate, duration):
    # Calculate number of samples
    num_samples = int(sample_rate * duration)
    
    # Generate white noise (Gaussian distribution)
    white_noise = np.random.normal(0, 1, num_samples)
    
    # Normalize to [-1, 1] range
    white_noise = white_noise / np.max(np.abs(white_noise))
    return white_noise

# Step 2: Apply compressor to increase perceived loudness (optional)
def apply_compressor(signal, threshold=0.9, ratio=2.0):
    """
    Apply dynamic range compression to boost loudness while controlling peaks.
    threshold: Amplitude above which compression starts (0.0 to 1.0, higher = less compression)
    ratio: Compression ratio (e.g., 2.0 means 2:1 compression, softer than 4.0)
    """
    output = signal.copy()
    for i in range(len(output)):
        if abs(output[i]) > threshold:
            sign = np.sign(output[i])
            excess = abs(output[i]) - threshold
            compressed_excess = excess / ratio
            output[i] = sign * (threshold + compressed_excess)
    return output

# Step 3: Save white noise as WAV file
def save_white_noise(white_noise, sample_rate, output_file):
    try:
        # Convert to 16-bit PCM format (standard for WAV)
        white_noise_int = np.int16(white_noise * 32767)
        wavfile.write(output_file, sample_rate, white_noise_int)
        print(f"Saved white noise to {output_file}")
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"File {output_file} created successfully, size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"Error: File {output_file} was not created properly")
    except Exception as e:
        print(f"Error saving file: {e}")

# Main execution
if __name__ == "__main__":
    # Generate white noise
    print(f"Generating white noise for {duration} seconds...")
    white_noise = generate_white_noise(sample_rate, duration)
    
    # Apply compressor if enabled
    if apply_compressor:
        white_noise = apply_compressor(white_noise, threshold=0.9, ratio=2.0)
        print("Applied compressor with softer settings")
    
    # Apply amplitude scaling
    white_noise = white_noise * amplitude
    print(f"Applied amplitude scaling: {amplitude}")
    
    # Ensure final signal is within [-1, 1] to avoid clipping
    white_noise = np.clip(white_noise, -1.0, 1.0)
    
    # Save to WAV file
    save_white_noise(white_noise, sample_rate, output_audio_file)