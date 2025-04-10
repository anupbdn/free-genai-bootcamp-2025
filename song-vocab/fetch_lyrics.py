import lyricsgenius
import langdetect  # To detect the language of lyrics
from langdetect import detect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# You'll need to get your own Genius API token from https://genius.com/api-clients
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

def fetch_lyrics_by_language(song_title, artist_name, target_language, max_songs=5):
    """
    Fetch lyrics for a song in a specific language
    
    Parameters:
    - song_title: Title of the song
    - artist_name: Name of the artist
    - target_language: Desired language code (e.g., 'en' for English, 'es' for Spanish)
    - max_songs: Maximum number of songs to search through
    
    Returns:
    - Dictionary with song details and lyrics if found, None if not found
    """
    try:
        # Initialize Genius API
        genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
        # Remove verbose output
        genius.verbose = False
        # Skip non-songs (interviews, etc.)
        genius.skip_non_songs = True
        
        # Search for songs by the artist
        artist = genius.search_artist(artist_name, max_songs=max_songs)
        
        if not artist:
            return f"No artist found with the name: {artist_name}"
            
        # Look for the specific song
        song = genius.search_song(song_title, artist_name)
        
        if not song:
            return f"No song found with the title: {song_title} by {artist_name}"
            
        # Get the lyrics
        lyrics = song.lyrics
        
        # Detect the language of the lyrics
        detected_language = detect(lyrics)
        
        if detected_language == target_language:
            return {
                'title': song.title,
                'artist': song.artist,
                'lyrics': lyrics,
                'language': detected_language
            }
        else:
            return f"Song found but lyrics are in {detected_language}, not {target_language}"
            
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    # Example usage
    song_title = input("Enter song title: ")
    artist_name = input("Enter artist name: ")
    target_language = input("Enter target language code (e.g., 'en' for English, 'es' for Spanish): ")
    
    result = fetch_lyrics_by_language(song_title, artist_name, target_language)
    
    if isinstance(result, dict):
        print(f"\nTitle: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"Language: {result['language']}")
        print("\nLyrics:")
        print(result['lyrics'])
    else:
        print(result)

if __name__ == "__main__":
    # Install required packages if not already installed
    # try:
    #     import pkg_resources
    # except ImportError:
    #     import subprocess
    #     subprocess.check_call(['pip', 'install', 'lyricsgenius', 'langdetect'])
    
    main()