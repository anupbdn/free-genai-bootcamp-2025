# Japanese Vocabulary Generator Tool

A Streamlit-based tool for generating Japanese vocabulary from English words or phrases using Mistral AI (via Ollama). This tool helps create structured vocabulary lists with Japanese translations, complete with readings, romaji, and hiragana parts.

## Features

- Generate Japanese vocabulary from English input using Mistral AI
- Export vocabulary to JSON format
- Import existing vocabulary from JSON files
- User-friendly Streamlit interface
- Support for both single words and phrases
- Includes romaji and hiragana parts breakdown

## Prerequisites

- Python 3.10 or higher
- Ollama installed and running locally
- Mistral model installed in Ollama locally in the machine either as a container using OPEA or run ollama directly

## Installation

1. Clone the repository
2. Install dependencies:
```bash
uv pip install -e .
```

3. Ensure Ollama is running and Mistral model is installed:
```bash
ollama list  # Check installed models
ollama show mistral:latest  # View model details
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run vocab_tool.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use either the "Generate Vocabulary" or "Import Vocabulary" tab

### Generate Vocabulary

1. Enter an English word or phrase in the text area
2. Click "Generate"
3. View the generated Japanese vocabulary with readings, romaji, and hiragana parts
4. Export to JSON if needed

### Import Vocabulary

1. Upload a JSON file containing vocabulary data
2. Review the imported vocabulary
3. Export modified vocabulary if needed

## Example Usage

### Example 1: Single Word
Input:
```
cat
```

Expected output:
```json
{
  "vocabulary": [
    {
      "japanese": "猫",
      "romaji": "neko",
      "english": "cat",
      "parts": {
        "hiragana": ["ね", "こ"]
      }
    }
  ]
}
```

### Example 2: Phrase
Input:
```
good morning
```

Expected output:
```json
{
  "vocabulary": [
    {
      "japanese": "おはよう",
      "romaji": "ohayou",
      "english": "good morning",
      "parts": {
        "hiragana": ["お", "は", "よ", "う"]
      }
    },
    {
      "japanese": "おはようございます",
      "romaji": "ohayou gozaimasu",
      "english": "good morning (polite)",
      "parts": {
        "hiragana": ["お", "は", "よ", "う", "ご", "ざ", "い", "ま", "す"]
      }
    }
  ]
}
```

## JSON Format

The tool expects and generates JSON in the following format:
```json
{
  "vocabulary": [
    {
      "japanese": "Japanese word",
      "romaji": "Romaji reading",
      "english": "English meaning",
      "parts": {
        "hiragana": ["h", "i", "r", "a", "g", "a", "n", "a", " ", "p", "a", "r", "t", "s"]
      }
    }
  ]
}
```

## Technical Details

- Uses Mistral AI model via Ollama
- API endpoint: `http://localhost:11434/api/generate`
- Streamlit interface for user interaction
- Regular expressions for parsing model output

## Troubleshooting

1. If the app can't connect to Ollama:
   - Ensure Ollama is running (`ollama serve`)
   - Check if Mistral model is installed (`ollama list`)

2. If no vocabulary is generated:
   - Check the input text format
   - Verify the model's response format
   - Try simpler input

3. If JSON import fails:
   - Verify the JSON format matches the expected structure
   - Check for valid UTF-8 encoding

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the same license as the Mistral model (Apache License 2.0). 