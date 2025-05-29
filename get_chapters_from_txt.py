import re
import os
import sys
from pathlib import Path

def replace_chapter_headings(text, toc):
    # Create a mapping of chapter numbers to titles from the table of contents
    chapter_map = {}
    for line in toc.splitlines():
        match = re.match(r'^(I{1,3}|IV|V|VI{0,3}|IX|X{1,3}|XIV|XV|XV?I{0,3}|XIX|XX|XXI|XXII|XXIII|XXIV)\.\s+([A-Z\s-]+)\s+\d+$', line.strip())
        if match:
            roman_num = match.group(1)
            title = match.group(2).strip()
            chapter_map[roman_num] = title
    
    # Function to convert Roman numeral to integer
    def roman_to_int(roman):
        roman_values = {'I': 1, 'V': 5, 'X': 10}
        result = 0
        prev_value = 0
        for char in reversed(roman):
            curr_value = roman_values[char]
            if curr_value >= prev_value:
                result += curr_value
            else:
                result -= curr_value
            prev_value = curr_value
        return result

    # Replace chapter headings in the text
    for roman, title in chapter_map.items():
        # Create the regex pattern for the chapter heading
        pattern = r'^\s+' + re.escape(roman + '.') + r'\s*\n\s*' + re.escape(title) + r'\.\s*$'
        # Create the replacement marker with chapter number and title
        chapter_num = roman_to_int(roman)
        replacement = f'[[chapter-{chapter_num}-start]]\nChapter {roman}. {title}.'
        # Replace the chapter heading
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    
    return text

def process_text_file(input_file, toc):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Read the input text file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Replace chapter headings
    modified_text = replace_chapter_headings(text, toc)
    
    # Generate output file path
    base_name = os.path.basename(input_file)  # e.g., "the_scarlet_letter.txt"
    filename =  Path(input_filename).stem
    output_dir = os.path.join("txts", filename)
    os.makedirs(output_dir, exist_ok=True)  # Create txts/chaptered if it doesn't exist
    output_file = os.path.join(output_dir, "chaptered.txt")  # e.g., txts/chaptered/the_scarlet_letter.txt
    
    # Save the modified text to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_text)
    
    print(f"Output saved to: {output_file}")
    
# TODO: This is just a wip with hardcoded TOC, will need to figure out how to make this dynamic

# Table of contents
toc = """I. THE PRISON-DOOR                                51
II. THE MARKET-PLACE                              54
III. THE RECOGNITION                              68
IV. THE INTERVIEW                                 80
V. HESTER AT HER NEEDLE                           90
VI. PEARL                                        104
VII. THE GOVERNOR’S HALL                         118
VIII. THE ELF-CHILD AND THE MINISTER             129
IX. THE LEECH                                    142
X. THE LEECH AND HIS PATIENT                     155
XI. THE INTERIOR OF A HEART                      168
XII. THE MINISTER’S VIGIL                        177
XIII. ANOTHER VIEW OF HESTER                     193
XIV. HESTER AND THE PHYSICIAN                    204
XV. HESTER AND PEARL                             212
XVI. A FOREST WALK                               223
XVII. THE PASTOR AND HIS PARISHIONER             231
XVIII. A FLOOD OF SUNSHINE                       245
XIX. THE CHILD AT THE BROOK-SIDE                 253
XX. THE MINISTER IN A MAZE                       264
XXI. THE NEW ENGLAND HOLIDAY                     277
XXII. THE PROCESSION                             288
XXIII. THE REVELATION OF THE SCARLET LETTER      302
XXIV. CONCLUSION                                 315"""

# Directory containing the input text file
input_dir = "input-txts"

# Specify the input file name (e.g., "the_scarlet_letter.txt")
input_filename = "test.txt"  # Change this to your input file name

filename = input("Enter which txt file to process from input-txts/: ")

# Construct the full path to the input file
input_file = os.path.join(input_dir, f"{filename}.txt")

# Process the specified text file
process_text_file(input_file, toc)