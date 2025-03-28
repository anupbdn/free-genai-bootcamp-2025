# Japanese Writing Practice App ✍️

## Purpose
The Japanese Writing Practice App is an interactive web application designed to help users learn and practice writing Japanese characters (Hiragana, Katakana, and Basic Kanji). The app provides a digital drawing canvas for practice, real-time character recognition for validation, and a knowledge testing system to track learning progress.

## Technical Details

### Drawing and Image Handling
- **Drawing Canvas**: Utilizes `streamlit-drawable-canvas` for interactive drawing functionality
  - Provides customizable stroke width and color
  - Supports freehand drawing mode
  - Canvas dimensions: 400x400 pixels
  - RGBA format with transparent background

- **Image Upload**:
  - Supports PNG, JPG, JPEG formats
  - Automatically resizes uploaded images to fit 400x400 dimensions
  - Maintains aspect ratio using Lanczos resampling

### Character Sets
The app includes three predefined character sets:
1. **Hiragana**: Basic Japanese syllabary (あ, い, う, etc.)
2. **Katakana**: Syllabary used for foreign words (ア, イ, ウ, etc.)
3. **Basic Kanji**: Fundamental Chinese characters (一, 二, 三, etc.)

Each character is stored with:
- The actual character (char)
- Its romanized reading (romaji)
- Additional context for Kanji (meanings in parentheses)

### Character Recognition System
The app uses a sophisticated OCR pipeline for character validation:

1. **Image Processing**:
   - Converts canvas RGBA data to RGB format
   - Applies white background for better OCR
   - Preserves stroke data using alpha channel masking

2. **OCR Implementation**:
   - Uses `manga-ocr` for Japanese character recognition
   - Converts detected characters to romaji using `pykakasi`
   - Provides detailed OCR feedback including:
     - Detected character
     - Romaji conversion
     - Match status
     - Accuracy metrics

## Setup and Running Instructions

### Prerequisites
- Python 3.13.1 or higher
- UV package manager

### Installation Steps

1. **Create and activate UV virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # For Unix/MacOS
   # or
   .venv\Scripts\activate  # For Windows
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run src/app.py
   ```

The app will open in your default web browser at `http://localhost:8501`

## Application Flow

![Application Flow Chart](assets/flow-chart.png)

The flow chart above illustrates the complete application workflow:
1. **Input Handling**: Users can either draw characters or upload images
2. **Processing Pipeline**: Both inputs go through image processing and OCR
3. **Character Sets**: Separate paths for Hiragana, Katakana, and Kanji practice
4. **Validation**: Matches are scored, and feedback is provided for non-matches

## Technical Requirements
- streamlit>=1.32.0
- streamlit-drawable-canvas>=0.9.3
- manga-ocr
- pykakasi>=2.2.1
- Pillow>=11.1.0
- numpy>=2.2.4
- python-magic>=0.4.27 