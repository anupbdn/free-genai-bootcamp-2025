from duckduckgo_search import DDGS
from langdetect import detect
from bs4 import BeautifulSoup
import requests
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
import json

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

@tool
def search_duckduckgo(query):
    """
    Search DuckDuckGo for lyrics URLs.
    Returns a list of result URLs.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))
            if not results:
                return []
            return [r['href'] for r in results]
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

@tool
def fetch_lyrics_with_duckduckgo(song_title: str, artist_name: str, target_language: str) -> Dict:
    """
    Fetch lyrics in a target language using DuckDuckGo.
    Args:
        song_title: Name of the song
        artist_name: Name of the artist
        target_language: ISO 639-1 language code (e.g., 'ja' for Japanese)
    Returns:
        Dictionary containing url, lyrics, and detected language
    """
    query = f"{song_title} {artist_name} lyrics"
    urls = search_duckduckgo(query)
    
    if not urls:
        return {"error": "No search results found"}
    
    for url in urls:
        lyrics = scrape_lyrics_from_url(url)
        if isinstance(lyrics, str) and "error" not in lyrics.lower():
            if not lyrics or len(lyrics.strip()) < 10:
                continue
                
            try:
                detected_language = detect(lyrics)
                if detected_language == target_language:
                    return {
                        'url': url,
                        'lyrics': lyrics,
                        'language': detected_language
                    }
            except Exception as e:
                continue
    
    return {"error": f"No lyrics found in {target_language}"}

@tool
def analyze_vocabulary(lyrics: str, target_language: str) -> Dict:
    """
    Analyze lyrics and create vocabulary guide.
    Args:
        lyrics: The lyrics text to analyze
        target_language: Target language code
    Returns:
        Dictionary containing vocabulary analysis
    """
    try:
        # Create Ollama chat prompt for vocabulary analysis
        prompt = f"""Analyze these lyrics in {target_language} and create a vocabulary guide.
        Return ONLY a JSON object with this structure:
        {{
            "words": [
                {{"word": "word", "meaning": "definition", "example": "usage"}}
            ],
            "phrases": [
                {{"phrase": "phrase", "meaning": "explanation"}}
            ],
            "cultural_references": [
                {{"reference": "reference", "explanation": "details"}}
            ]
        }}
        
        Lyrics: {lyrics}
        """
        
        # Call Ollama API
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        result = response.json()
        return json.loads(result['response'])
    except Exception as e:
        return {"error": f"Vocabulary analysis failed: {str(e)}"}

class SongVocabAgent:
    """
    Agent for managing song vocabulary analysis workflow.
    """
    def __init__(self):
        # Initialize Ollama model
        self.llm = ChatOllama(model="mistral")
        
        # Define available tools
        self.tools = [
            search_duckduckgo,
            fetch_lyrics_with_duckduckgo,
            analyze_vocabulary
        ]
        
        # Create conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Define the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful music vocabulary assistant. You can:
            1. Find song lyrics in different languages
            2. Analyze vocabulary and phrases from lyrics
            3. Explain cultural references
            
            Always confirm the language before processing and verify the song details.
            If a task fails, explain why and suggest alternatives."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=prompt,
            tools=self.tools
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    def process_request(self, user_input: str) -> str:
        """
        Process user request and return response.
        Args:
            user_input: User's query or request
        Returns:
            Agent's response
        """
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"Error processing request: {str(e)}"

def main():
    # Initialize the agent
    agent = SongVocabAgent()
    
    print("Song Vocabulary Assistant (type 'quit' to exit)")
    print("Example: 'Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese'")
    
    while True:
        user_input = input("\nYour request: ").strip()
        if user_input.lower() == 'quit':
            break
            
        response = agent.process_request(user_input)
        print("\nAssistant:", response)

if __name__ == "__main__":
    main()
            