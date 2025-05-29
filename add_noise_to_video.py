import os
import glob
import sys
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.VideoClip import VideoClip
import time
import numpy as np
from scipy.io import wavfile

def add_noise_to_video(video_path, audio_path, output_dir="videos_with_audio"):
    print(f"Processing video: {video_path}, audio: {audio_path}")
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        return None
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found.")
        return None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        # Load video
        print("Loading video...")
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration
        video_fps = video_clip.fps
        print(f"Loaded video '{video_path}' with duration {video_duration:.2f} seconds, fps {video_fps}")

        # Load audio
        print("Loading audio...")
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        sample_rate = audio_clip.fps
        print(f"Loaded noise '{audio_path}' with duration {audio_duration:.2f} seconds, sample rate {sample_rate}")

        # Check input audio volume
        input_volume = audio_clip.max_volume()
        print(f"Input WAV max volume: {input_volume:.4f}")
        if input_volume < 0.01:
            print(f"Warning: Input WAV '{audio_path}' has very low or zero volume.")

        # Adjust volume
        audio_name = os.path.basename(audio_path).lower()
        volume_factor = 1.0 if 'brown_noise' in audio_name else 0.5
        print(f"Applying {volume_factor*100:.0f}% volume for {audio_name}")

        # Scale volume
        clip_data = audio_clip.to_soundarray()
        max_amplitude = np.max(np.abs(clip_data))
        if max_amplitude > 0:
            clip_data = clip_data / max_amplitude
        else:
            print(f"Error: Input audio '{audio_name}' has zero amplitude.")
        clip_data = clip_data * volume_factor
        audio_clip.close()

        # Save temporary WAV
        temp_wav = f"temp_scaled_{audio_name}.wav"
        wavfile.write(temp_wav, sample_rate, np.int16(clip_data * 32767))
        print(f"Saved temporary WAV: {temp_wav}")

        # Verify temp WAV
        audio_clip = AudioFileClip(temp_wav)
        temp_volume = audio_clip.max_volume()
        print(f"Temporary WAV max volume: {temp_volume:.4f}")

        # Match audio duration to video
        if audio_duration < video_duration:
            num_repeats = int(video_duration / audio_duration) + 1
            audio_clips = [AudioFileClip(temp_wav) for _ in range(num_repeats)]
            audio_clip = CompositeAudioClip(audio_clips)
            print(f"Noise '{audio_path}' repeated {num_repeats} times to cover {video_duration:.2f} seconds")
            # Verify composite audio duration
            composite_duration = audio_clip.duration
            print(f"Composite audio duration: {composite_duration:.2f} seconds")
            if composite_duration < video_duration:
                print(f"Warning: Composite audio duration ({composite_duration:.2f}s) is shorter than video ({video_duration:.2f}s)")
        else:
            audio_clip = audio_clip.set_duration(video_duration)
            print(f"Noise '{audio_path}' trimmed to {video_duration:.2f} seconds")

        # Set audio on video clip using with_audio
        final_clip = video_clip.with_audio(audio_clip)
        if final_clip.audio is None:
            print("Error: Audio was not properly attached to the final clip.")
            raise ValueError("Audio attachment failed")

        # Output file
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_filename = f"{video_name}_{audio_name}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        print(f"Writing video to '{output_path}'...")

        # Write video (compatible with older MoviePy versions)
        final_clip.write_videofile(
            output_path,
            fps=video_fps,
            codec="libx264",
            audio_codec="aac",
            audio_bitrate="192k",
            bitrate="1000k",
            threads=2,
            temp_audiofile="temp_audio.wav",
            remove_temp=True
        )

        # Verify output file
        if os.path.exists(output_path):
            print(f"Output file created: {output_path}, size: {os.path.getsize(output_path)} bytes")
        else:
            print(f"Error: Output file '{output_path}' was not created.")

        # Cleanup
        video_clip.close()
        final_clip.close()
        audio_clip.close()
        for clip in audio_clips if 'audio_clips' in locals() else []:
            clip.close()
        # if os.path.exists(temp_wav):
        #     os.remove(temp_wav)
        print(f"Video with noise saved to '{output_path}'")
        return output_path
    except Exception as e:
        print(f"Error processing video or audio for '{audio_path}': {e}")
        if 'video_clip' in locals():
            video_clip.close()
        if 'final_clip' in locals():
            final_clip.close()
        if 'audio_clip' in locals():
            audio_clip.close()
        if 'audio_clips' in locals():
            for clip in audio_clips:
                clip.close()
        if 'temp_wav' in locals() and os.path.exists(temp_wav):
            os.remove(temp_wav)
        return None
def process_all_wavs(video_path, audio_dir="audio", output_dir="videos_with_audio"):
    """
    Process all .wav files in audio_dir, creating a new video for each with the input video.
    
    Args:
        video_path (str): Path to the input video file.
        audio_dir (str): Directory containing .wav files (default: 'audio').
        output_dir (str): Directory for output videos (default: 'videos_with_audio').
    
    Returns:
        list: Paths to the created videos, or empty list if errors occur.
    """
    start_time = time.time()
    output_paths = []

    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory '{audio_dir}' not found.")
        return output_paths

    wav_files = glob.glob(os.path.join(audio_dir, "*.wav"))
    if not wav_files:
        print(f"No .wav files found in '{audio_dir}'.")
        return output_paths

    print(f"Found {len(wav_files)} .wav files: {', '.join(os.path.basename(f) for f in wav_files)}")

    for wav_file in wav_files:
        print(f"\nProcessing '{wav_file}'...")
        result = add_noise_to_video(video_path, wav_file, output_dir)
        if result:
            output_paths.append(result)

    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(int(execution_time), 60)
    print(f"\nCompleted processing. Total execution time: {minutes:02d}:{seconds:02d} (minutes:seconds)")
    return output_paths

if __name__ == "__main__":
    video_input_dir = "videos"
    audio_dir = "audio"
    output_dir = "videos_with_audio"

    # Default to test.mp4, allow override via command-line argument
    video_filename = "test.mp4"
    if len(sys.argv) > 1:
        video_filename = sys.argv[1].strip()
    if not video_filename.lower().endswith('.mp4'):
        video_filename += '.mp4'
    video_path = os.path.join(video_input_dir, video_filename)

    results = process_all_wavs(video_path, audio_dir, output_dir)
    if results:
        print("Created videos:")
        for path in results:
            print(f"- {path}")
    else:
        print("No videos were created. Check inputs and try again.")