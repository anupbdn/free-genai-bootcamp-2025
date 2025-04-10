import requests
import json
from typing import List, Dict
import re
from langdetect import detect, LangDetectException

def clean_lyrics(lyrics: str) -> str:
    """
    Clean the lyrics by removing unnecessary elements and formatting.
    """
    # Remove common patterns in lyrics that we don't need
    patterns_to_remove = [
        r'\[.*?\]',  # Remove [Verse], [Chorus] etc.
        r'\(.*?\)',  # Remove (repeat) etc.
        r'\d+$',     # Remove trailing numbers
        r'^\d+\.',   # Remove leading numbers with dots
    ]
    
    cleaned_lyrics = lyrics
    for pattern in patterns_to_remove:
        cleaned_lyrics = re.sub(pattern, '', cleaned_lyrics)
    
    # Remove empty lines and extra whitespace
    cleaned_lines = [line.strip() for line in cleaned_lyrics.split('\n') if line.strip()]
    return '\n'.join(cleaned_lines)

def detect_language_safe(text: str, default: str = 'unknown') -> str:
    """
    Safely detect language of text with fallback.
    """
    try:
        if not text or len(text.strip()) < 10:
            return default
        return detect(text)
    except LangDetectException:
        return default

def chunk_lyrics(lyrics: str, target_language: str, chunk_size: int = 200) -> List[Dict[str, str]]:
    """
    Split lyrics into smaller chunks while preserving line integrity and language detection.
    Args:
        lyrics: The complete lyrics text
        target_language: Target language code (e.g., 'ja' for Japanese)
        chunk_size: Approximate number of characters per chunk
    Returns:
        List of dictionaries containing chunks and their detected language
    """
    cleaned_lyrics = clean_lyrics(lyrics)
    lines = cleaned_lyrics.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_length = len(line)
        
        if current_length + line_length > chunk_size and current_chunk:
            # Process current chunk
            chunk_text = '\n'.join(current_chunk)
            detected_lang = detect_language_safe(chunk_text)
            if detected_lang == target_language:
                chunks.append({
                    'text': chunk_text,
                    'language': detected_lang
                })
            # Start a new chunk
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length
    
    # Process the last chunk if it exists
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        detected_lang = detect_language_safe(chunk_text)
        if detected_lang == target_language:
            chunks.append({
                'text': chunk_text,
                'language': detected_lang
            })
    
    return chunks

def get_vocabulary_from_ollama(text: str, model_name: str = "mistral") -> Dict:
    """
    Send text to Ollama model and get vocabulary analysis.
    Args:
        text: Text chunk to analyze
        model_name: Name of the Ollama model to use
    Returns:
        Dictionary containing vocabulary analysis
    """
    prompt = f"""Analyze these lyrics and create a vocabulary guide. You MUST include ALL fields (word, meaning, example) for each entry.
    Respond ONLY with a valid JSON object in this EXACT format, no other text:
    {{
        "words": [
            {{"word": "word here", "meaning": "definition here", "example": "usage in context here"}}
        ],
        "phrases": [
            {{"phrase": "phrase here", "meaning": "explanation here"}}
        ],
        "cultural_references": [
            {{"reference": "reference here", "explanation": "details here"}}
        ]
    }}

    Lyrics to analyze:
    {text}
    """
    
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": model_name,
                                   "prompt": prompt,
                                   "stream": False
                               })
        response.raise_for_status()
        result = response.json()
        
        # Try to extract JSON from the response
        try:
            # First attempt: direct JSON parsing
            parsed_result = json.loads(result['response'])
        except json.JSONDecodeError:
            # Second attempt: try to find and extract JSON object
            response_text = result['response']
            try:
                # Find JSON-like structure between curly braces
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed_result = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("No JSON found", response_text, 0)
            except json.JSONDecodeError:
                return {
                    "words": [{"word": "Error", "meaning": "Could not parse model output", "example": "N/A"}],
                    "phrases": [],
                    "cultural_references": []
                }
        
        # Ensure all required fields are present
        sanitized_result = {
            "words": [],
            "phrases": [],
            "cultural_references": []
        }
        
        # Sanitize words
        for word in parsed_result.get("words", []):
            if isinstance(word, dict):
                sanitized_result["words"].append({
                    "word": word.get("word", "Unknown"),
                    "meaning": word.get("meaning", "No meaning provided"),
                    "example": word.get("example", "No example provided")
                })
        
        # Sanitize phrases
        for phrase in parsed_result.get("phrases", []):
            if isinstance(phrase, dict):
                sanitized_result["phrases"].append({
                    "phrase": phrase.get("phrase", "Unknown"),
                    "meaning": phrase.get("meaning", "No meaning provided")
                })
        
        # Sanitize cultural references
        for ref in parsed_result.get("cultural_references", []):
            if isinstance(ref, dict):
                sanitized_result["cultural_references"].append({
                    "reference": ref.get("reference", "Unknown"),
                    "explanation": ref.get("explanation", "No explanation provided")
                })
        
        return sanitized_result
                
    except Exception as e:
        print(f"Error calling Ollama API: {str(e)}")
        return {
            "words": [],
            "phrases": [],
            "cultural_references": [],
            "error": str(e)
        }

def process_lyrics_for_vocabulary(lyrics: str, target_language: str, model_name: str = "mistral") -> List[Dict]:
    """
    Process complete lyrics and generate vocabulary analysis.
    Args:
        lyrics: Complete lyrics text
        target_language: Target language code (e.g., 'ja' for Japanese)
        model_name: Name of the Ollama model to use
    Returns:
        List of vocabulary analysis for each chunk
    """
    # Split lyrics into chunks with language detection
    chunks = chunk_lyrics(lyrics, target_language)
    vocabulary_results = []
    
    if not chunks:
        print(f"No chunks found in target language: {target_language}")
        return vocabulary_results
    
    # Process each chunk in target language
    for chunk in chunks:
        result = get_vocabulary_from_ollama(chunk['text'], model_name)
        if "error" not in result:
            vocabulary_results.append(result)
    
    return vocabulary_results

def main():
    # Example usage
    from fetch_ddg import fetch_lyrics_with_duckduckgo
    
    # Get lyrics
    song_title = input("Enter song title: ")
    artist_name = input("Enter artist name: ")
    target_language = input("Enter target language code (e.g., 'ja' for Japanese): ")
    
    result = fetch_lyrics_with_duckduckgo(song_title, artist_name, target_language)
    
    if isinstance(result, dict):
        print("\nProcessing lyrics for vocabulary...")
        print(f"Looking for chunks in {target_language}...")
        
        vocabulary_analysis = process_lyrics_for_vocabulary(result['lyrics'], target_language)
        
        if not vocabulary_analysis:
            print(f"\nNo lyrics found in target language: {target_language}")
            return
            
        # Print results
        print(f"\nVocabulary Analysis (Language: {target_language}):")
        for i, chunk_analysis in enumerate(vocabulary_analysis, 1):
            print(f"\nChunk {i}:")
            
            # Print words section
            if chunk_analysis.get('words'):
                print("Words:")
                for word in chunk_analysis['words']:
                    print(f"- {word.get('word', 'Unknown')}: {word.get('meaning', 'No meaning provided')}")
                    if word.get('example') and word['example'] != "No example provided":
                        print(f"  Example: {word['example']}")
            
            # Print phrases section
            if chunk_analysis.get('phrases'):
                print("\nPhrases:")
                for phrase in chunk_analysis['phrases']:
                    print(f"- {phrase.get('phrase', 'Unknown')}: {phrase.get('meaning', 'No meaning provided')}")
            
            # Print cultural references section
            if chunk_analysis.get('cultural_references'):
                print("\nCultural References:")
                for ref in chunk_analysis['cultural_references']:
                    print(f"- {ref.get('reference', 'Unknown')}: {ref.get('explanation', 'No explanation provided')}")
    else:
        print(result)

if __name__ == "__main__":
    main() 