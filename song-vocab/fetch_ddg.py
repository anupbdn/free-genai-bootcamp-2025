import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS  # DuckDuckGo search library
from langdetect import detect

def search_duckduckgo(query):
    """
    Search DuckDuckGo for lyrics URLs.
    Returns a list of result URLs.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))  # Convert iterator to list and increase max_results
            if not results:
                return []
            return [r['href'] for r in results]
    except Exception as e:
        print(f"Search error: {str(e)}")  # Print the error for debugging
        return []

def scrape_lyrics_from_url(url):
    """
    Scrape lyrics from a given URL.
    Returns the lyrics text or an error message.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style']):
            element.decompose()
        
        # Common lyrics selectors for different websites
        lyrics = None
        
        # Try different common selectors used by lyrics websites
        selectors = [
            'div[class*="lyrics"]',  # Classes containing "lyrics"
            'div[class*="Lyrics"]',
            'div[id*="lyrics"]',     # IDs containing "lyrics"
            'div[id*="Lyrics"]',
            '.lyrics-body',          # Common class names
            '.lyrics-content',
            '.lyric-body',
            '.song-lyrics',
            'div[class*="song_body"]',
            'div[class*="songtext"]',
            'div.content'            # Generic content div
        ]
        
        # Try each selector
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                lyrics = element.get_text(separator='\n').strip()
                if lyrics and len(lyrics) > 50:  # Ensure we have substantial content
                    break
        
        # If no lyrics found with selectors, try paragraph tags within main content
        if not lyrics:
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                paragraphs = main_content.find_all('p')
                lyrics = '\n'.join(p.get_text() for p in paragraphs)
        
        # If still no lyrics, try pre tags
        if not lyrics:
            pre_tag = soup.find('pre')
            if pre_tag:
                lyrics = pre_tag.get_text()
        
        if lyrics and len(lyrics.strip()) > 50:  # Minimum 50 characters to ensure it's actual lyrics
            # Clean up the lyrics
            lyrics = '\n'.join(line.strip() for line in lyrics.split('\n') if line.strip())
            return lyrics
        else:
            return "No lyrics found on this page"
            
    except requests.RequestException as e:
        return f"Scraping error: Connection failed - {str(e)}"
    except Exception as e:
        return f"Scraping error: {str(e)}"

def fetch_lyrics_with_duckduckgo(song_title, artist_name, target_language):
    """
    Fetch lyrics in a target language using DuckDuckGo.
    Parameters:
    - song_title: Song name
    - artist_name: Artist name
    - target_language: ISO 639-1 code (e.g., 'ml' for Malayalam, 'ja' for Japanese)
    """
    # Construct search query - simplified
    query = f"{song_title} {artist_name} lyrics"
    urls = search_duckduckgo(query)
    
    if not urls:
        return "No search results found. Please try again with a different search query."
    
    # Try each URL until we find lyrics in the target language
    for url in urls:
        lyrics = scrape_lyrics_from_url(url)
        if isinstance(lyrics, str) and "error" not in lyrics.lower():
            # Check if lyrics is not empty and has enough content
            if not lyrics or len(lyrics.strip()) < 10:  # Minimum 10 characters
                print(f"Skipping {url} - insufficient content")
                continue
                
            try:
                detected_language = detect(lyrics)
                if detected_language == target_language:
                    return {
                        'url': url,
                        'lyrics': lyrics,
                        'language': detected_language
                    }
                else:
                    print(f"Found lyrics at {url}, but language is {detected_language}, not {target_language}")
            except Exception as e:
                print(f"Language detection failed for {url}: {str(e)}")
                continue
    
    return f"No lyrics found in {target_language}"

def main():
    # Install required packages if not already installed
    # try:
    #     import pkg_resources
    # except ImportError:
    #     import subprocess
    #     subprocess.check_call(['pip', 'install', 'duckduckgo-search', 'beautifulsoup4', 'langdetect', 'requests'])
    
    # User input
    song_title = input("Enter song title: ")
    artist_name = input("Enter artist name: ")
    target_language = input("Enter target language code (e.g., 'ml' for Malayalam, 'ja' for Japanese): ")
    
    # Fetch lyrics
    result = fetch_lyrics_with_duckduckgo(song_title, artist_name, target_language)
    
    if isinstance(result, dict):
        print(f"\nSource URL: {result['url']}")
        print(f"Detected Language: {result['language']}")
        print("\nLyrics:")
        print(result['lyrics'])
    else:
        print(result)

if __name__ == "__main__":
    main()