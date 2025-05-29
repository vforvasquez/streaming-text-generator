import numpy as np
from scipy.io import wavfile

# Parameters
sample_rate = 44100  # Hz (standard audio sampling rate)
duration = 60.0      # seconds (adjust as needed)
output_audio_file = "brown_noise.wav"

# Step 1: Generate brown noise
def generate_brown_noise(sample_rate, duration):
    # Calculate number of samples
    num_samples = int(sample_rate * duration)
    
    # Generate white noise (Gaussian distribution)
    white_noise = np.random.normal(0, 1, num_samples)
    
    # Integrate white noise to produce brown noise
    brown_noise = np.cumsum(white_noise)
    
    # Normalize to [-1, 1] range to prevent clipping, with 50% amplitude for safety
    brown_noise = brown_noise / np.max(np.abs(brown_noise)) * .5
    return brown_noise

# Step 2: Save brown noise as WAV file
def save_brown_noise(brown_noise, sample_rate, output_file):
    # Convert to 16-bit PCM format (standard for WAV)
    brown_noise_int = np.int16(brown_noise * 32767)
    wavfile.write(output_file, sample_rate, brown_noise_int)
    print(f"Saved brown noise to: {output_file}")

# Main execution
if __name__ == "__main__":
    # Generate brown noise
    brown_noise = generate_brown_noise(sample_rate, duration)
    
    # Save to WAV file
    save_brown_noise(brown_noise, sample_rate, output_audio_file)