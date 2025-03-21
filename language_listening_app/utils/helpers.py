"""
Helper utility functions for the Language Listening App
"""
import re
from datetime import timedelta
import html

def format_time(seconds):
    """Format seconds into human readable time (MM:SS)"""
    return str(timedelta(seconds=seconds))[2:7]  # HH:MM:SS -> MM:SS

def sanitize_input(text):
    """Sanitize user input to prevent security issues"""
    if text is None:
        return ""
    # Escape HTML tags and special characters
    text = html.escape(text)
    # Remove any potential script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    return text

def validate_url(url):
    """Validate if a URL is a valid YouTube URL"""
    if not url:
        return False
    
    # Simple regex for YouTube URLs
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?\s]{11})'
    )
    
    match = re.match(youtube_regex, url)
    return match is not None 