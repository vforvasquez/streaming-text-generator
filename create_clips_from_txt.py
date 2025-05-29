import re
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.video.VideoClip import VideoClip
import os
import psutil
import time
import sys
import datetime

# Global constant for words per chunk
WORDS_PER_CHUNK = 1

# Function to log run details (assumed implementation)
def log_run_details(script_name, book_title, runtime):
    """
    Log the run details to run_details.txt, converting runtime from seconds to MM:SS format.
    
    Args:
        script_name (str): Name of the Python script.
        book_title (str): Book title provided by the user.
        runtime (float): Time taken to run the script in seconds.
    """
    try:
        # Convert runtime (seconds) to minutes and seconds
        minutes, seconds = divmod(int(runtime), 60)
        runtime_str = f"{minutes:02d}:{seconds:02d}"
        
        # Get current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Format the log entry
        log_entry = f"Date: {current_time}, Script: {script_name}, Book Title: {book_title}, Runtime: {runtime_str} (minutes:seconds)\n"
        # Append to run_details.txt
        with open("run_details.txt", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error writing to run_details.txt: {e}")

# Step 1: Extract text and chapter data from text file
def extract_text_and_chapters_from_text(text_path):
    try:
        with open(text_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading text file: {e}")
        return None, None, None

    # Log first few lines for debugging
    print("First 5 lines of text file:")
    for i, line in enumerate(lines[:5]):
        print(f"Line {i+1}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")

    full_text = ""
    chapter_positions = []
    chapter_titles = []
    word_count = 0

    # Regex to match [[chapter-<number>-start]]
    chapter_pattern = re.compile(r'\[\[chapter-(\d+)-start\]\]', re.IGNORECASE)
    # Secondary regex to match chapter titles (e.g., "Chapter I. THE PRISON-DOOR")
    title_pattern = re.compile(r'Chapter\s+(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX|XXI|XXII|XXIII|XXIV)\.\s*([^\n]+)', re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        match = chapter_pattern.match(line)
        if match:
            chapter_num = match.group(1)
            # Try to find a chapter title in the same line (after the marker) or the next line
            title = None
            title_match = title_pattern.search(line)  # Check same line
            if title_match:
                roman_num = title_match.group(1)
                title_text = title_match.group(2).strip()
                title = f"Chapter {roman_num}. {title_text}"
            elif i + 1 < len(lines):
                # Check next line
                next_line = lines[i + 1].strip()
                title_match = title_pattern.match(next_line)
                if title_match:
                    roman_num = title_match.group(1)
                    title_text = title_match.group(2).strip()
                    title = f"Chapter {roman_num}. {title_text}"
                    i += 1  # Skip the title line

            # Fallback title if none found
            if not title:
                title = f"Chapter {chapter_num}"
                print(f"No title found for [[chapter-{chapter_num}-start]], using default: {title}")
            else:
                print(f"Detected chapter: [[chapter-{chapter_num}-start]] {title} at word {word_count}")

            chapter_positions.append((chapter_num, word_count))
            chapter_titles.append(title)
            i += 1
            continue

        # Log potential chapter-like lines for debugging
        if line.lower().startswith('chapter') or '[[' in line:
            print(f"Potential chapter line not matched: {line[:100]}{'...' if len(line) > 100 else ''}")
        full_text += line + " "
        word_count += len(line.split())
        i += 1

    if not chapter_positions:
        chapter_positions.append(("1", 0))
        chapter_titles.append("Start")
        print("No chapters detected. Treating the entire text as a single section.")

    print(f"Total chapters detected: {len(chapter_positions)}")
    print(f"Total words in text: {word_count}")
    return full_text, chapter_positions, chapter_titles

# Step 2: Chunk text into segments
def chunk_text(text, words_per_chunk=WORDS_PER_CHUNK):
    if not text:
        return []
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    chunks = [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
    print(f"Total chunks created: {len(chunks)}")
    return chunks

# Step 3: Map chapter positions to chunk indices
def map_chapters_to_chunks(chapter_positions, chunks, words_per_chunk=WORDS_PER_CHUNK):
    chapter_indices = []
    for chapter_num, word_count in chapter_positions:
        chunk_index = word_count // words_per_chunk
        if chunk_index < len(chunks):
            chapter_indices.append(chunk_index)
            print(f"Chapter {chapter_num} mapped to chunk index {chunk_index}")
        else:
            print(f"Warning: Chapter {chapter_num} word count {word_count} maps to invalid chunk index {chunk_index}")
    print(f"Total chapter indices: {len(chapter_indices)}")
    return chapter_indices

# Step 4: Create a styled title frame for each chapter
def create_title_frame(book_title, author, chapter_title, width=640, height=360, watermark_text="Generated by {user name}"):
    image = Image.new("RGB", (width, height), color=(20, 20, 40))  # Dark blue background
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("arial.ttf", 40)
        subtitle_font = ImageFont.truetype("arial.ttf", 30)
        watermark_font = ImageFont.truetype("arial.ttf", 15)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    # Book title (top, 1/6 height)
    title_bbox = draw.textbbox((0, 0), book_title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_position = ((width - title_width) // 2, height // 6 - title_height // 2)
    draw.text(title_position, book_title, fill=(255, 255, 200), font=title_font)  # Light cream text

    # Author (middle, 1/2 height)
    author_text = f"by {author}"
    author_bbox = draw.textbbox((0, 0), author_text, font=subtitle_font)
    author_width = author_bbox[2] - author_bbox[0]
    author_height = author_bbox[3] - author_bbox[1]
    author_position = ((width - author_width) // 2, height // 2 - author_height // 2)
    draw.text(author_position, author_text, fill=(200, 200, 255), font=subtitle_font)  # Light blue text

    # Chapter title (underneath, 5/6 height)
    chapter_bbox = draw.textbbox((0, 0), chapter_title, font=subtitle_font)
    chapter_width = chapter_bbox[2] - chapter_bbox[0]
    chapter_height = chapter_bbox[3] - chapter_bbox[1]
    chapter_position = ((width - chapter_width) // 2, 5 * height // 6 - chapter_height // 2)
    draw.text(chapter_position, chapter_title, fill=(200, 200, 255), font=subtitle_font)  # Light blue text

    # Watermark (bottom-right)
    watermark_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    watermark_height = watermark_bbox[3] - watermark_bbox[1]
    watermark_position = (width - watermark_width - 10, height - watermark_height - 10)
    draw.text(watermark_position, watermark_text, fill=(128, 128, 128), font=watermark_font)

    return np.array(image)

# Step 5: Create a frame with text and watermark
def create_text_frame(text, width=640, height=360, font_size=30, watermark_text="Generated by {your name here}"):
    image = Image.new("RGB", (width, height), color="black")
    draw = ImageDraw.Draw(image)
    try:
        main_font = ImageFont.truetype("arial.ttf", font_size)
        watermark_font = ImageFont.truetype("arial.ttf", 15)
    except:
        main_font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=main_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(text_position, text, fill="white", font=main_font)

    watermark_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    watermark_height = watermark_bbox[3] - watermark_bbox[1]
    watermark_position = (width - watermark_width - 10, height - watermark_height - 10)
    draw.text(watermark_position, watermark_text, fill=(128, 128, 128), font=watermark_font)
    
    return np.array(image)

# Step 6: Create a video clip for a single chapter
def create_chapter_video(book_title, author, chunks, chapter_index, next_chapter_index, chapter_title, chapter_num, output_path, fps=24, wpm=450):
    title_duration = 3  # Title frame duration
    duration_per_chunk = (60 / wpm) * WORDS_PER_CHUNK
    num_chunks = next_chapter_index - chapter_index if next_chapter_index is not None else len(chunks) - chapter_index
    total_duration = title_duration + num_chunks * duration_per_chunk

    def make_frame(t):
        if t < title_duration:
            return create_title_frame(book_title, author, chapter_title)
        adjusted_t = t - title_duration
        chunk_offset = int(adjusted_t / duration_per_chunk)
        if chunk_offset >= num_chunks:
            return create_text_frame("")  # Blank frame at end
        chunk_idx = chapter_index + chunk_offset
        if chunk_idx >= len(chunks):
            return create_text_frame("")
        if chunk_idx % 1000 == 0:
            print(f"Processing chunk {chunk_idx}/{len(chunks)} for chapter {chapter_num} - Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
        return create_text_frame(chunks[chunk_idx])

    print(f"Generating video for chapter {chapter_num}, {num_chunks} chunks, duration {total_duration:.2f} seconds...")
    try:
        clip = VideoClip(make_frame, duration=total_duration)
        clip.write_videofile(output_path, codec="libx264", fps=fps, bitrate="1000k", threads=4,
                            temp_audiofile=f"temp_audio_{chapter_num}.mp3", remove_temp=True)
        clip.close()
        print(f"Video saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error during video creation for chapter {chapter_num}: {e}")
        if 'clip' in locals():
            clip.close()
        return False

# Step 7: Main execution
if __name__ == "__main__":
    start_time = time.time()
    texts_dir = "txts"
    chaptered_file_name = "chaptered.txt"
    script_name = os.path.basename(__file__)
    
    text_filename = input("Enter the name of the text file (e.g., 'test.txt'): ").strip()
    if not text_filename.lower().endswith('.txt'):
        text_filename += '.txt'
    # Remove .txt extension for directory name
    base_filename = os.path.splitext(text_filename)[0]
    text_path = os.path.join(texts_dir, base_filename, chaptered_file_name)

    book_title = input("Enter the book title: ").strip()
    author = input("Enter the author name: ").strip()

    if not os.path.exists(texts_dir):
        print(f"Error: '{texts_dir}' directory not found. Please create it and place your text files there.")
        exit(1)

    if not os.path.exists(text_path):
        print(f"Error: '{text_path}' not found in the '{texts_dir}' directory.")
        exit(1)

    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage before processing: {mem_before:.2f} MB")
    available_memory = psutil.virtual_memory().available / 1024 / 1024
    print(f"Available memory: {available_memory:.2f} MB")
    if available_memory < 1000:
        print("Warning: Low available memory. Consider increasing WORDS_PER_CHUNK.")

    book_text, chapter_positions, chapter_titles = extract_text_and_chapters_from_text(text_path)
    if book_text is None or chapter_positions is None:
        print("Failed to process text file. Exiting.")
        exit(1)

    chunks = chunk_text(book_text)
    chapter_indices = map_chapters_to_chunks(chapter_positions, chunks)
    total_words = len(book_text.split())
    
    if not chapter_positions:
        print("No chapters detected. Treating as single section.")
        chapter_indices = [0]
        chapter_positions = [("1", 0)]
        chapter_titles = ["Start"]

    # Create output directory
    output_dir = os.path.join("videos", base_filename, "chapters")
    os.makedirs(output_dir, exist_ok=True)

    # Generate video for each chapter
    successful_videos = 0
    for i in range(len(chapter_indices)):
        chapter_num = chapter_positions[i][0]
        chapter_title = chapter_titles[i]
        chapter_idx = chapter_indices[i]
        next_chapter_idx = chapter_indices[i + 1] if i + 1 < len(chapter_indices) else None
        output_filename = f"{base_filename}-{chapter_num}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        print(f"Starting video creation for chapter {chapter_num}: {chapter_title}")
        if create_chapter_video(book_title, author, chunks, chapter_idx, next_chapter_idx, chapter_title, chapter_num, output_path):
            successful_videos += 1
        else:
            print(f"Failed to create video for chapter {chapter_num}")

    print(f"Created {successful_videos} out of {len(chapter_indices)} chapter videos")
    mem_after = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage after processing: {mem_after:.2f} MB")
    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(int(execution_time), 60)
    print(f"Total execution time: {minutes:02d}:{seconds:02d} (minutes:seconds)")
    
    # Log run details with execution_time (float in seconds)
    log_run_details(script_name, book_title, execution_time)