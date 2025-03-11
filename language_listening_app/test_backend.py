#!/usr/bin/env python
"""
Test script for the Language Listening App backend
This script tests the main functionality of the backend components
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the backend components
from backend.app_service import AppService

# Load environment variables
load_dotenv()

def test_process_video():
    """Test processing a YouTube video and generating questions"""
    print("\n=== Testing Video Processing ===")
    
    # Initialize the app service
    app_service = AppService()
    
    # Process a short educational video (TED-Ed)
    video_url = "https://www.youtube.com/watch?v=0e0duD8_LFE"  # A short TED-Ed video
    
    print(f"Processing video: {video_url}")
    print("This may take a minute or two...")
    
    try:
        # Use Ollama by default as it doesn't require AWS credentials
        question_set = app_service.process_video(
            url=video_url,
            language="en",
            provider="ollama"
        )
        
        print(f"\nSuccessfully processed video!")
        print(f"Video ID: {question_set.transcript_id}")
        print(f"Generated {len(question_set.questions)} questions")
        
        # Print a few sample questions
        print("\nSample questions:")
        for i, question in enumerate(question_set.questions[:3], 1):
            print(f"\nQuestion {i}: {question.text}")
            print(f"Answer: {question.answer}")
            print(f"Explanation: {question.explanation}")
            print(f"Difficulty: {question.difficulty}")
        
        return question_set
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def test_search(question_set):
    """Test searching for similar content"""
    if not question_set:
        print("\nSkipping search test as video processing failed")
        return
    
    print("\n=== Testing Search Functionality ===")
    
    # Initialize the app service
    app_service = AppService()
    
    # Get a search query from the first question
    search_query = question_set.questions[0].text
    print(f"Searching for: '{search_query}'")
    
    try:
        # Search for similar questions
        similar_questions = app_service.search_similar_questions(search_query)
        
        print(f"\nFound {len(similar_questions)} similar questions:")
        for i, result in enumerate(similar_questions, 1):
            print(f"\nResult {i}: {result['text']}")
            print(f"Distance: {result['distance']}")
        
        # Search for similar chunks
        similar_chunks = app_service.search_similar_chunks(search_query)
        
        print(f"\nFound {len(similar_chunks)} similar transcript chunks:")
        for i, result in enumerate(similar_chunks, 1):
            print(f"\nResult {i}: {result['text'][:100]}...")
            print(f"Distance: {result['distance']}")
    except Exception as e:
        print(f"Error searching: {e}")

def main():
    """Main function to run all tests"""
    print("=== Language Listening App Backend Test ===")
    
    # Test video processing
    question_set = test_process_video()
    
    # Test search functionality
    test_search(question_set)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()