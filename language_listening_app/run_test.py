#!/usr/bin/env python
"""
Runner script for testing the Language Listening App backend
This script properly imports and runs the backend components
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the necessary components using absolute imports
from language_listening_app.backend.app_service import AppService
from language_listening_app.models.schemas import Question, QuestionSet

def test_process_video():
    """Test processing a YouTube video and generating questions"""
    print("\n=== Testing Video Processing ===")
    
    # Initialize the app service
    app_service = AppService()
    
    # Use the original video URL
    video_url = "https://www.youtube.com/watch?v=0e0duD8_LFE"  # Original video URL
    
    print(f"Processing video: {video_url}")
    print("This may take a minute or two...")
    
    # Test with Bedrock
    print("\n--- Testing Amazon Bedrock ---")
    
    # First, test the Bedrock connection
    try:
        # Import boto3 for direct testing
        import boto3
        from botocore.config import Config
        import json
        import os
        
        # Get AWS credentials from environment
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Create Bedrock client
        bedrock_config = Config(
            region_name=aws_region,
            retries={"max_attempts": 3}
        )
        
        bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=bedrock_config
        )
        
        # Try a simple test request with Amazon Nova
        model_id = "amazon.nova-micro-v1:0"  # Using Nova Micro as in your .env file
        
        print(f"Testing connection to AWS Bedrock with model: {model_id}")
        
        # Use the correct request format for Amazon models
        response = bedrock_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "inferenceConfig": {
                    "max_new_tokens": 100
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": "Hello, can you hear me?"
                            }
                        ]
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response.get("body").read())
        print("Bedrock connection successful!")
        print("Response preview:", str(response_body)[:100] + "...")
        
        # Now try processing the video with Bedrock
        print("\nProcessing video with Bedrock...")
        
        # Try different languages
        languages = ["en", "ja"]
        bedrock_question_set = None
        
        for language in languages:
            try:
                print(f"\nTrying language: {language}")
                
                bedrock_question_set = app_service.process_video(
                    url=video_url,
                    language=language,
                    provider="bedrock",
                    model="amazon.nova-micro-v1:0"  # Explicitly specify the model
                )
                
                print(f"\nSuccessfully processed video with Bedrock in {language}!")
                print(f"Video ID: {bedrock_question_set.transcript_id}")
                print(f"Generated {len(bedrock_question_set.questions)} questions")
                
                # Print a few sample questions
                print("\nSample questions:")
                for i, question in enumerate(bedrock_question_set.questions[:3], 1):
                    print(f"\nQuestion {i}: {question.text}")
                    print(f"Answer: {question.answer}")
                    print(f"Explanation: {question.explanation}")
                    print(f"Difficulty: {question.difficulty}")
                
                # If we successfully processed the video, break the loop
                break
            except Exception as e:
                print(f"Error processing video with Bedrock in {language}: {e}")
        
        if bedrock_question_set is None:
            print("\nFailed to process video with Bedrock in any language.")
            
    except Exception as e:
        print(f"Error testing Bedrock connection: {e}")
    
    # Test with Ollama
    print("\n--- Testing Ollama ---")
    
    # Try processing the video with Ollama
    print("\nProcessing video with Ollama...")
    
    # Try different languages
    languages = ["en", "ja"]
    ollama_question_set = None
    
    for language in languages:
        try:
            print(f"\nTrying language: {language}")
            
            ollama_question_set = app_service.process_video(
                url=video_url,
                language=language,
                provider="ollama",
                model="mistral:latest"  # Explicitly specify the model
            )
            
            print(f"\nSuccessfully processed video with Ollama in {language}!")
            print(f"Video ID: {ollama_question_set.transcript_id}")
            print(f"Generated {len(ollama_question_set.questions)} questions")
            
            # Print a few sample questions
            print("\nSample questions:")
            for i, question in enumerate(ollama_question_set.questions[:3], 1):
                print(f"\nQuestion {i}: {question.text}")
                print(f"Answer: {question.answer}")
                print(f"Explanation: {question.explanation}")
                print(f"Difficulty: {question.difficulty}")
            
            # If we successfully processed the video, break the loop
            break
        except Exception as e:
            print(f"Error processing video with Ollama in {language}: {e}")
    
    if ollama_question_set is None:
        print("\nFailed to process video with Ollama in any language.")
    
    # Return the question set from either provider (prioritize Bedrock)
    return bedrock_question_set or ollama_question_set

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

def test_vector_store(question_set):
    """Test storing and retrieving data from the vector store"""
    if not question_set:
        print("\n=== Skipping Vector Store Test (No Question Set Available) ===")
        return
    
    print("\n=== Testing Vector Store ===")
    
    # Import the necessary components
    from language_listening_app.backend.vector_store import VectorStoreManager
    
    # Initialize the vector store manager
    vector_store = VectorStoreManager()
    
    # Verify that the transcript is in the vector store
    print("\nChecking if transcript is in vector store...")
    transcript_id = question_set.transcript_id
    
    # Get all transcripts
    all_transcripts = vector_store.get_all_transcripts()
    transcript_found = any(t.video_id == transcript_id for t in all_transcripts)
    
    if transcript_found:
        print(f"✅ Transcript {transcript_id} found in vector store!")
    else:
        print(f"❌ Transcript {transcript_id} not found in vector store.")
    
    # Verify that questions are in the vector store
    print("\nChecking if questions are in vector store...")
    
    # Get all questions for this transcript
    all_questions = vector_store.get_questions_for_transcript(transcript_id)
    
    if all_questions:
        print(f"✅ Found {len(all_questions)} questions for transcript {transcript_id} in vector store!")
        
        # Print a few sample questions from the vector store
        print("\nSample questions from vector store:")
        for i, question in enumerate(all_questions[:3], 1):
            print(f"\nQuestion {i}: {question.text}")
            print(f"Answer: {question.answer}")
            print(f"Explanation: {question.explanation}")
            print(f"Difficulty: {question.difficulty}")
    else:
        print(f"❌ No questions found for transcript {transcript_id} in vector store.")
    
    # Test semantic search
    print("\nTesting semantic search...")
    query = "What is the main topic of the video?"
    
    # Search for similar questions
    similar_questions = vector_store.search_similar_questions(query, n_results=3)
    
    if similar_questions:
        print(f"✅ Found {len(similar_questions)} similar questions for query: '{query}'")
        
        # Print the similar questions
        print("\nSimilar questions:")
        for i, result in enumerate(similar_questions, 1):
            question = result["question"]
            score = result["score"]
            print(f"\nQuestion {i} (Score: {score:.2f}): {question.text}")
            print(f"Answer: {question.answer}")
    else:
        print(f"❌ No similar questions found for query: '{query}'")
    
    # Search for similar chunks
    similar_chunks = vector_store.search_similar_chunks(query, n_results=3)
    
    if similar_chunks:
        print(f"\n✅ Found {len(similar_chunks)} similar transcript chunks for query: '{query}'")
        
        # Print the similar chunks
        print("\nSimilar chunks:")
        for i, result in enumerate(similar_chunks, 1):
            chunk = result["chunk"]
            score = result["score"]
            print(f"\nChunk {i} (Score: {score:.2f}): {chunk.text[:100]}...")
    else:
        print(f"\n❌ No similar transcript chunks found for query: '{query}'")
    
    return True

def main():
    """Main function to run all tests"""
    print("=== Language Listening App Backend Test ===")
    
    # Test video processing
    question_set = test_process_video()
    
    # Test search functionality
    test_search(question_set)
    
    # Test vector store
    test_vector_store(question_set)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 