# Streaming Text Generator

Welcome to the **Streaming Text Generator**! This Python project processes text files to generate structured output, such as chaptered text files, with optional image generation capabilities. The main script, `create_stv_from_txt.py`, reads an input text file from `input-txts/` and outputs a processed file to `txt/{filename}/chaptered.txt`.

## Features
- **Text Processing**: Reads a user-specified text file (e.g., `input-txts/test.txt`) and generates a processed output (e.g., `txt/test/chaptered.txt`).
- **Image Generation**: Utilizes the `Pillow` library for potential image creation or manipulation (if applicable).
- **Isolated Environments**: Uses Python virtual environments to manage dependencies without affecting system-wide installations.
- **User-Friendly Input**: Prompts users to specify input filenames for flexible file processing.

## Prerequisites
- **Python 3.6+**: Ensure Python 3 is installed (`python3 --version`).
- **Operating System**: Tested on Linux (e.g., Ubuntu). Windows and macOS should work with minor adjustments.
- **Dependencies**:
  - `numpy`: For numerical computations.
  - `Pillow`: For image processing.
  - Additional dependencies may be listed in `requirements.txt` (if present).

## Installation

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/vforvasquez/streaming-text-generator.git
cd streaming-text-generator
```

### 2. Set Up a Virtual Environment
Create and activate a Python virtual environment to isolate dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install numpy Pillow
```

If a requirements.txt file is present, install all dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Script
The main script, `create_stv_from_txt.py`, prompts for a filename and processes a text file from the `input-txts/` directory.

1. **Prepare an Input File**:
   Place your input text file in the `input-txts/` directory. For example:
   ```bash
   mkdir -p input-txts
   echo "Sample content" > input-txts/test.txt
    ```
   
2. **Run the Script**:
	Ensure the virtual environment is activated:
	```bash
	source venv/bin/activate
	python create_stv_from_txt.py

3. **Enter Filename**:
	When prompted, enter the filename without the .txt extension (e.g., test for input-txts/test.txt):
	```bash
	Enter the filename (without .txt, e.g., 'test' for input-txts/test.txt): test

4. **Check Output**:
	The script processes the input file and writes the output to txt/test/chaptered.txt. Verify the output:
	```bash
	cat txt/test/chaptered.txt

## Directory Structure
```bash
	streaming-text-generator/
	├── input-txts/              # Input text files (e.g., test.txt)
	├── txt/                     # Output directories (e.g., txt/test/chaptered.txt)
	├── venv/                    # Virtual environment
	├── create_stv_from_txt.py   # Main script
	├── requirements.txt         # (Optional) Dependency list
	└── README.md                # This file

