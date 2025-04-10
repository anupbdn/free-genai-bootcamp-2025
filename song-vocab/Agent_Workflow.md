# Song Vocabulary Agent Workflow

## 1. Purpose of the Agent

The Song Vocabulary Agent is an AI-powered assistant designed to help users learn vocabulary from songs in different languages. It combines:
- Lyrics fetching capabilities
- Language detection
- Vocabulary analysis
- Cultural context understanding

This makes it particularly useful for:
- Language learners using music as a learning tool
- Music enthusiasts interested in understanding lyrics in different languages
- Teachers preparing song-based language learning materials
- Anyone interested in understanding the cultural context of songs

## 2. Agent Capabilities

### Core Functions:
1. **Lyrics Search and Retrieval**
   - Search for song lyrics across multiple websites
   - Filter results by target language
   - Handle multiple song versions and translations

2. **Language Processing**
   - Detect song language automatically
   - Verify if lyrics match requested language
   - Handle multiple language codes (e.g., 'ja' for Japanese, 'es' for Spanish)

3. **Vocabulary Analysis**
   - Extract important words and phrases
   - Provide definitions and explanations
   - Give usage examples in context
   - Identify cultural references

4. **Conversation Management**
   - Remember context from previous queries
   - Handle follow-up questions
   - Provide clarifications when needed

## 3. How the Agent Works

### High-Level Architecture:

[agent workflow](agent_workflow.png)

### Workflow Steps:

1. **Input Processing**
   - User provides song details and target language
   - Agent parses the request and identifies required actions

2. **Lyrics Retrieval**
   - Searches for lyrics using DuckDuckGo
   - Scrapes lyrics from found URLs
   - Validates content and language

3. **Language Verification**
   - Confirms lyrics are in requested language
   - Filters out non-matching content
   - Ensures quality of retrieved text

4. **Vocabulary Analysis**
   - Processes lyrics through Ollama model
   - Extracts vocabulary items
   - Identifies phrases and cultural references
   - Generates explanations and examples

5. **Response Generation**
   - Formats analysis results
   - Provides structured vocabulary guide
   - Includes context and usage examples

## 4. How to Use the Agent

### Setup Requirements:
```bash
# Install required packages
pip install langchain langchain-community duckduckgo-search beautifulsoup4 langdetect requests

# Ensure Ollama is running with Mistral model
ollama run mistral
```

### Basic Usage:
1. **Start the Agent**
   ```bash
   python song_agent.py
   ```

2. **Example Queries**:
   ```
   > Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese
   > Explain the cultural references in the song
   > What are the key phrases used?
   ```

### Query Format:
- Song title and artist: `"[Song Name] by [Artist]"`
- Specify language: `"in [language]"` or `"[language] lyrics"`
- Ask for specific analysis: `"vocabulary"`, `"phrases"`, `"cultural references"`

### Example Session:
```
Your request: Find vocabulary from Sukiyaki by Kyu Sakamoto in Japanese
Assistant: Searching for lyrics...
Found lyrics in Japanese. Analyzing vocabulary...
[Vocabulary analysis results...]

Your request: What are the cultural references in this song?
Assistant: Analyzing cultural context...
[Cultural reference explanations...]
```

### Tips for Best Results:
1. Be specific about the song and artist
2. Always specify the target language
3. Use follow-up questions for deeper understanding
4. Ask about specific aspects (words, phrases, culture)

### Error Handling:
- If lyrics aren't found, try alternative song titles
- If language detection fails, verify the song's language
- For better results, use official song titles in their original language

## Note:
The agent uses Ollama's Mistral model for analysis, ensuring:
- Privacy (all processing is local)
- Customizable responses
- No API key requirements
- Fast response times 