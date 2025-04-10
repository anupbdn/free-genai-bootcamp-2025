from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from song_agent import SongVocabAgent
import uvicorn
import json
import re

app = FastAPI(
    title="Song Vocabulary API",
    description="API for fetching song lyrics and analyzing vocabulary",
    version="1.0.0"
)

# Initialize the agent
agent = SongVocabAgent()

class LyricsRequest(BaseModel):
    message_request: str

class VocabularyItem(BaseModel):
    word: str
    meaning: str
    example: Optional[str] = None

class LyricsResponse(BaseModel):
    lyrics: str
    vocabulary: List[Dict]
    phrases: List[Dict]
    cultural_references: List[Dict]

def extract_vocabulary_from_text(text: str) -> Dict[str, List[Dict]]:
    """
    Extract vocabulary items from text response.
    Args:
        text: The text response from the agent
    Returns:
        Dictionary containing structured vocabulary data
    """
    result = {
        "vocabulary": [],
        "phrases": [],
        "cultural_references": []
    }
    
    # Extract Japanese-English word pairs (pattern: Japanese (romaji) - English)
    word_pattern = r'(\d+\.\s+)?([^\s-]+)\s+\(([^)]+)\)\s+-\s+([^,\n]+)'
    matches = re.finditer(word_pattern, text)
    
    for match in matches:
        word_jp = match.group(2)
        romaji = match.group(3)
        meaning = match.group(4).strip()
        
        result["vocabulary"].append({
            "word": word_jp,
            "romaji": romaji,
            "meaning": meaning,
            "example": f"{word_jp} ({romaji})"
        })
    
    # Extract phrases if present (looking for patterns like "phrase: meaning" or "phrase - meaning")
    phrase_pattern = r'([^:]+):\s+([^\n]+)'
    phrases = re.finditer(phrase_pattern, text)
    for phrase in phrases:
        if not any(word['word'] in phrase.group(1) for word in result['vocabulary']):
            result["phrases"].append({
                "phrase": phrase.group(1).strip(),
                "meaning": phrase.group(2).strip()
            })
    
    # Look for cultural references (typically in parentheses or after "Note:" or "Cultural reference:")
    cultural_ref_pattern = r'(?:Note:|Cultural reference:)\s+([^\n]+)'
    cultural_refs = re.finditer(cultural_ref_pattern, text)
    for ref in cultural_refs:
        result["cultural_references"].append({
            "reference": "Cultural Note",
            "explanation": ref.group(1).strip()
        })
    
    return result

@app.post("/api/agent", response_model=LyricsResponse)
async def get_lyrics(request: LyricsRequest):
    """
    Get lyrics and vocabulary analysis for a song.
    
    Parameters:
    - message_request: A string describing the song and artist (e.g., "Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese")
    
    Returns:
    - lyrics: The song lyrics
    - vocabulary: List of vocabulary items with meanings and examples
    - phrases: List of phrases with explanations
    - cultural_references: List of cultural references with explanations
    """
    try:
        # Process the request using our agent
        response = agent.process_request(request.message_request)
        
        # Initialize default response structure
        result = {
            "lyrics": "",
            "vocabulary": [],
            "phrases": [],
            "cultural_references": []
        }
        
        # Try to parse the agent's response
        try:
            # First try to parse as JSON
            if isinstance(response, str):
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        json_str = response[json_start:json_end]
                        parsed_response = json.loads(json_str)
                        
                        if isinstance(parsed_response, dict):
                            if 'lyrics' in parsed_response:
                                result['lyrics'] = parsed_response['lyrics']
                            if 'words' in parsed_response:
                                result['vocabulary'] = parsed_response['words']
                            if 'phrases' in parsed_response:
                                result['phrases'] = parsed_response['phrases']
                            if 'cultural_references' in parsed_response:
                                result['cultural_references'] = parsed_response['cultural_references']
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract structured data from text
                        extracted_data = extract_vocabulary_from_text(response)
                        result.update(extracted_data)
                        
                        # Store original text as lyrics if we couldn't parse JSON
                        if not result['lyrics']:
                            result['lyrics'] = response
                else:
                    # No JSON found, try to extract structured data from text
                    extracted_data = extract_vocabulary_from_text(response)
                    result.update(extracted_data)
                    result['lyrics'] = response
                    
        except Exception as parsing_error:
            print(f"Parsing error: {str(parsing_error)}")
            # If all parsing fails, return raw response as lyrics
            result['lyrics'] = response
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Song Vocabulary API",
        "version": "1.0.0",
        "endpoints": {
            "/api/agent": "POST - Get lyrics and vocabulary analysis"
        }
    }

def start():
    """Start the FastAPI server using uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start() 