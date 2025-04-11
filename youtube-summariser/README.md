# YouTube Video Summarizer

A Python application that automatically generates concise summaries of YouTube videos using their transcripts and advanced natural language processing.

## Purpose

This application helps users quickly understand the content of YouTube videos by providing AI-generated summaries of the video transcripts. It's particularly useful for:
- Getting the key points of long videos quickly
- Research and content analysis
- Making decisions about whether to watch the full video
- Educational purposes and study aids

## Features

- **YouTube Transcript Extraction**: Automatically fetches transcripts from any YouTube video
- **Smart Text Processing**: 
  - Handles videos of any length through intelligent text chunking
  - Implements overlap between chunks to maintain context
  - Uses recursive summarization for longer content
- **Flexible Summary Generation**: Creates concise, coherent summaries while preserving key information
- **URL Support**: Works with both standard YouTube URLs (youtube.com) and shortened URLs (youtu.be)
- **Categorisation of Content**: From the final summary of the content, content will be categorised as chapters of whole summary for you to read.

## Tech Stack

- **Python**: Core programming language
- **youtube_transcript_api**: For fetching YouTube video transcripts
- **transformers (Hugging Face)**: For text summarization
  - Uses the BART-large-CNN model for high-quality summarization
- **urllib**: For parsing and validating YouTube URLs
- **ollama**: For using locally running mistral

## How to Use

1. **Setup**:
   ```bash
   # Install required packages
   uv sync --active
   ```

2. **Running the Application**:
   ```bash
   source .venv/bin/activate
   uv run youtube_summariser.py
   ```

3. **Usage Steps**:
   - Launch the application
   - Enter a YouTube video URL when prompted
   - Wait for the summary to be generated
   - Read the generated summary

Note: The video must have available transcripts/subtitles for the summarizer to work.

## Limitations
- Requires videos to have available transcripts
- Processing time may vary based on video length
- Quality of summary depends on transcript quality and content type 