import os
import subprocess
import logging
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio
from dataclasses import dataclass
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.Clip import Clip
from moviepy.decorators import audio_video_effect
from moviepy.Effect import Effect

# Define AudioLoop effect
@dataclass
class AudioLoop(Effect):
    """Loops over an audio clip."""
    n_loops: int = None
    duration: float = None

    @audio_video_effect
    def apply(self, clip: Clip) -> Clip:
        if self.duration is not None:
            self.n_loops = int(self.duration / clip.duration) + 1
            return concatenate_audioclips(self.n_loops * [clip]).with_duration(self.duration)
        return concatenate_audioclips(self.n_loops * [clip])

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

# File paths
# Use relative paths (assumes 'videos', 'audio', and 'videos_with_audio' folders are in the same directory as the script)
video_dir = os.path.join(os.path.dirname(__file__), "videos")
audio_dir = os.path.join(os.path.dirname(__file__), "audio")
output_dir = os.path.join(os.path.dirname(__file__), "videos_with_audio")
temp_audio_path = "temp_looped_audio.mp3"

def check_ffmpeg():
    """Verify FFmpeg installation and codec support."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        logger.debug(f"FFmpeg version: {result.stdout.splitlines()[0]}")
        codecs = subprocess.run(["ffmpeg", "-codecs"], capture_output=True, text=True)
        has_aac = "aac" in codecs.stdout.lower()
        has_mp3 = "mp3" in codecs.stdout.lower()
        logger.debug(f"FFmpeg supports AAC: {has_aac}, MP3: {has_mp3}")
        if not (has_aac and has_mp3):
            logger.error("FFmpeg missing required codecs (AAC or MP3)")
            return False
        return True
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg and add it to PATH.")
        return False

def inspect_file(file_path):
    """Inspect file properties using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-show_streams", "-show_format", file_path],
            capture_output=True, text=True
        )
        logger.debug(f"ffprobe output for {file_path}:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"ffprobe failed for {file_path}: {e}")
        return None

def process_video_with_audio(audio_filename, video_filename):
    """Process video with specified audio file and track execution time."""
    # Record start time
    start_time = time.time()
    
    video_path = os.path.join(video_dir, video_filename)
    audio_path = os.path.join(audio_dir, audio_filename)
    # Combine video and audio filenames (without extensions) for output
    video_basename = os.path.splitext(os.path.basename(video_filename))[0]
    audio_basename = os.path.splitext(os.path.basename(audio_filename))[0]
    output_filename = f"{video_basename}_{audio_basename}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Log the paths being used
    logger.info(f"Video path: {video_path}")
    logger.info(f"Audio path: {audio_path}")
    logger.info(f"Output path: {output_path}")
    
    # Verify input files exist
    logger.info("Checking input files...")
    if not os.path.exists(video_path):
        logger.error(f"Video file {video_path} not found")
        raise FileNotFoundError(f"Video file {video_path} not found")
    if not os.path.exists(audio_path):
        logger.error(f"Audio file {audio_path} not found")
        raise FileNotFoundError(f"Audio file {audio_path} not found")

    # Verify FFmpeg
    logger.info("Verifying FFmpeg installation...")
    if not check_ffmpeg():
        raise RuntimeError("FFmpeg verification failed")

    # Inspect input files
    logger.info(f"Inspecting {video_path}...")
    inspect_file(video_path)
    logger.info(f"Inspecting {audio_path}...")
    inspect_file(audio_path)

    try:
        # Load video and audio files
        logger.info("Loading video and audio files...")
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        # Log file details
        logger.info(f"Video duration: {video.duration} seconds, FPS: {video.fps}, Size: {video.size}")
        logger.info(f"Audio duration: {audio.duration} seconds, Channels: {audio.nchannels}")
        if video.audio is not None:
            logger.warning("Video already has audio. It will be replaced.")

        # Handle audio duration mismatch
        if audio.duration < video.duration:
            logger.warning(f"Audio ({audio.duration}s) is shorter than video ({video.duration}s). Looping audio.")
            looped_audio = audio.with_effects([AudioLoop(duration=video.duration)])
            logger.info(f"Saving looped audio to {temp_audio_path}")
            looped_audio.write_audiofile(temp_audio_path, codec="mp3")
            audio.close()  # Close original audio
            audio = AudioFileClip(temp_audio_path)  # Load looped audio
            audio_path = temp_audio_path
            logger.info(f"Looped audio duration: {audio.duration} seconds")
        elif audio.duration > video.duration:
            logger.warning(f"Audio ({audio.duration}s) is longer than video ({video.duration}s). Trimming audio.")
            audio = audio.with_duration(video.duration)  # Use with_duration for trimming
            logger.info(f"Trimmed audio duration: {audio.duration} seconds")

        # Close video clip as not needed for ffmpeg_merge_video_audio
        video.close()

        # Merge video and audio
        logger.info(f"Merging video ({video_path}) and audio ({audio_path}) into {output_path}")
        try:
            ffmpeg_merge_video_audio(
                video_path,
                audio_path,
                output_path,
                video_codec="copy",
                audio_codec="aac",
                logger="bar"
            )

        except Exception as e:
            logger.error(f"ffmpeg_merge_video_audio failed: {e}")
            raise

        # Verify output file
        logger.info(f"Verifying output file {output_path}...")
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"Output file created: {output_path}, Size: {os.path.getsize(output_path)} bytes")
            ffprobe_output = inspect_file(output_path)
            if ffprobe_output and "audio" in ffprobe_output.lower():
                logger.info("Audio stream detected in output file")
            else:
                logger.warning("No audio stream detected in output file")
        else:
            logger.error(f"Output file {output_path} was not created or is empty")
            raise RuntimeError(f"Output file {output_path} was not created properly")

    except Exception as e:
        logger.error(f"Error processing video with ffmpeg_merge_video_audio: {e}")
        raise

    finally:
        # Close audio clip
        try:
            audio.close()
        except NameError:
            pass

        # Clean up temporary files
        for temp_file in [temp_audio_path]:
            if os.path.exists(temp_file):
                logger.info(f"Cleaning up temporary file: {temp_file}")
                os.remove(temp_file)

        # Log total execution time
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

# Example usage
if __name__ == "__main__":
    audio_file = "white_noise.mp3"  # Replace with desired audio file name
    video_file = "pride_and_prejudice.mp4"  # Replace with desired video file name
    process_video_with_audio(audio_file, video_file)