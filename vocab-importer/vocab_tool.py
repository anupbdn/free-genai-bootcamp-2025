import streamlit as st
import requests
import json
import re
import speech_recognition as sr
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
import os
import tempfile
import base64
import boto3
from botocore.config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # Default to us-east-1 if not set

# Debug logging for AWS credentials
st.sidebar.write("AWS Configuration:")
st.sidebar.write(f"Region: {AWS_REGION}")
st.sidebar.write(f"Access Key ID: {AWS_ACCESS_KEY_ID[:5]}...{AWS_ACCESS_KEY_ID[-4:] if AWS_ACCESS_KEY_ID else 'None'}")
st.sidebar.write(f"Secret Key: {'*' * 8}...{'*' * 4}")

# Check if AWS credentials are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    st.warning("AWS credentials not found in environment variables. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")

# Ollama API endpoint for Mistral
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# AWS Bedrock configuration
def test_bedrock_connection():
    try:
        client = get_bedrock_client()
        # Try a simple test request with the correct format for Amazon Nova
        response = client.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "inferenceConfig": {
                    "max_new_tokens": 1000
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": "Hello"
                            }
                        ]
                    }
                ]
            })
        )
        return True, "Successfully connected to AWS Bedrock!"
    except Exception as e:
        return False, f"Failed to connect to AWS Bedrock: {str(e)}"

def get_bedrock_client():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    
    bedrock_config = Config(
        region_name=AWS_REGION,
        retries={"max_attempts": 3}
    )
    return boto3.client(
        'bedrock-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=bedrock_config
    )

def query_bedrock(prompt, model_id="amazon.nova-micro-v1:0"):
    client = get_bedrock_client()
    try:
        # Different request formats for different models
        if model_id.startswith("anthropic"):
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:"]
            }
        else:  # amazon models
            request_body = {
                "inferenceConfig": {
                    "max_new_tokens": 1000
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        response_body = json.loads(response.get('body').read())
        
        # Different response formats for different models
        if model_id.startswith("anthropic"):
            return response_body.get("completion", "No response generated")
        else:  # amazon models
            # Handle Amazon Nova model response format
            if "output" in response_body and "message" in response_body["output"]:
                content = response_body["output"]["message"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "No response generated")
            return "No response generated"
            
    except Exception as e:
        return f"Error querying Bedrock: {str(e)}"

# Function to query LLM (either Ollama or Bedrock)
def query_llm(prompt, model_type="ollama", model_id="mistral:latest"):
    if model_type == "ollama":
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            return "Error: The model took too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to the Ollama service. Please make sure Ollama is running."
        except requests.exceptions.RequestException as e:
            return f"Error generating content: {str(e)}"
    else:  # Bedrock
        return query_bedrock(prompt, model_id)

# Function to query Mistral via Ollama
def get_vocab_from_ollama(text):
    # Different prompts for different model types
    if st.session_state.get("model_type") == "bedrock":
        prompt = (
            f"You are a Japanese language expert. Given this English word or phrase, provide the Japanese translation with its reading in hiragana and romaji. "
            f"Format each item as 'japanese (hiragana) [romaji]: english'. "
            f"If there are multiple common translations, provide the most relevant ones. "
            f"Example: '猫 (ねこ) [neko]: cat'. "
            f"Text to translate: {text}"
        )
        # Get the selected model ID from the session state
        model_id = st.session_state.get("bedrock_model", "amazon.nova-micro-v1:0")
    else:  # ollama
        prompt = (
            f"Given this English word or phrase, provide the Japanese translation with its reading in hiragana and romaji. "
            f"Format each item as 'japanese (hiragana) [romaji]: english'. "
            f"If there are multiple common translations, provide the most relevant ones. "
            f"Example: '猫 (ねこ) [neko]: cat'. Text: {text}"
        )
        model_id = st.session_state.get("ollama_model", "mistral:latest")
    
    raw_output = query_llm(prompt, model_type=st.session_state.get("model_type", "ollama"), model_id=model_id)
    
    # Handle different model responses
    if st.session_state.get("model_type") == "bedrock":
        # For Bedrock, the response might be wrapped in a different format
        if isinstance(raw_output, str):
            # Try to parse the response as JSON if it's a string
            try:
                raw_output = json.loads(raw_output)
            except json.JSONDecodeError:
                # If it's not JSON, use it as is
                pass
    
    return parse_mistral_output(raw_output)

# Parse Mistral's text output into structured JSON
def parse_mistral_output(output):
    # Handle different output formats
    if isinstance(output, dict):
        # If output is already a dictionary, try to extract the text
        if "messages" in output and len(output["messages"]) > 0:
            content = output["messages"][0]["content"]
            if isinstance(content, list) and len(content) > 0:
                output = content[0].get("text", "")
            else:
                output = str(content)
        elif "completion" in output:
            output = output["completion"]
        else:
            output = str(output)
    
    # Expected output example: "猫 (ねこ) [neko]: cat\n好き (すき) [suki]: like"
    vocab_list = []
    lines = output.strip().split("\n")
    
    for line in lines:
        # Use regex to extract word, reading, romaji, and meaning
        match = re.search(r"(.+?)\s*\((.+?)\)\s*\[(.+?)\]:\s*(.+)", line)
        if match:
            japanese, hiragana, romaji, english = match.groups()
            # Split hiragana into individual characters
            hiragana_parts = list(hiragana.strip())
            vocab_list.append({
                "japanese": japanese.strip(),
                "romaji": romaji.strip(),
                "english": english.strip(),
                "parts": {
                    "hiragana": hiragana_parts
                }
            })
    
    return {"vocabulary": vocab_list}

# Speech to Text function
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results"

# YouTube Transcript function
def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error getting transcript: {str(e)}"

def generate_dialogues_and_questions(transcript):
    prompt = f"""Based on this transcript, generate:
1. A natural dialogue that captures the main points
2. 3 comprehension questions with answers

Transcript: {transcript}

Format the response as:
DIALOGUE:
[Your dialogue here]

QUESTIONS:
1. [Question 1]
Answer: [Answer 1]

2. [Question 2]
Answer: [Answer 2]

3. [Question 3]
Answer: [Answer 3]"""
    
    return query_llm(prompt, model_type=st.session_state.get("model_type", "ollama"))

# Text to Speech function
def text_to_speech(text, language='ja'):
    tts = gTTS(text=text, lang=language)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name

# Streamlit app
st.title("Japanese Language Learning Tools")

# Model selection in sidebar
st.sidebar.title("Model Settings")
model_type = st.sidebar.selectbox(
    "Select Model Provider",
    ["ollama", "bedrock"],
    key="model_type"
)

if model_type == "ollama":
    model_id = st.sidebar.selectbox(
        "Select Ollama Model",
        ["mistral:latest", "llama2:latest", "codellama:latest"],
        key="ollama_model"
    )
else:  # bedrock
    model_id = st.sidebar.selectbox(
        "Select Bedrock Model",
        ["amazon.nova-micro-v1:0", "anthropic.claude-v2", "anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-haiku-20240307-v1:0"],
        key="bedrock_model"
    )
    
    # Add test connection button for Bedrock
    if st.sidebar.button("Test Bedrock Connection"):
        success, message = test_bedrock_connection()
        if success:
            st.sidebar.success(message)
        else:
            st.sidebar.error(message)

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Features",
    ["Generate Vocabulary", "Import Vocabulary", "Speech to Text", "YouTube Transcript", "Text to Speech"]
)

# Main content area
if page == "Generate Vocabulary":
    st.subheader("Generate Vocabulary")
    input_text = st.text_area("Enter English word or phrase", "", key="generate_input")
    
    if st.button("Generate", key="generate_btn"):
        if input_text:
            # Get the current model name for the spinner message
            model_type = st.session_state.get("model_type", "ollama")
            model_id = st.session_state.get(f"{model_type}_model", "mistral:latest")
            spinner_message = f"Generating Japanese vocabulary with {model_id}..."
            
            with st.spinner(spinner_message):
                vocab_data = get_vocab_from_ollama(input_text)
                if vocab_data and vocab_data["vocabulary"]:
                    st.session_state["generated_vocab"] = vocab_data
                    st.success("Vocabulary generated successfully!")
                    st.json(vocab_data)
                else:
                    st.warning("No vocabulary generated. Check the input or model output.")
        else:
            st.error("Please enter some text!")

    # Export option if vocabulary is generated
    if "generated_vocab" in st.session_state:
        json_str = json.dumps(st.session_state["generated_vocab"], ensure_ascii=False, indent=2)
        st.download_button(
            label="Export to JSON",
            data=json_str,
            file_name="japanese_vocab.json",
            mime="application/json",
            key="export_btn"
        )

elif page == "Import Vocabulary":
    st.subheader("Import Vocabulary")
    uploaded_file = st.file_uploader("Upload a JSON vocabulary file", type=["json"], key="import_file")
    
    if uploaded_file:
        try:
            vocab_data = json.load(uploaded_file)
            if "vocabulary" in vocab_data and isinstance(vocab_data["vocabulary"], list):
                st.session_state["imported_vocab"] = vocab_data
                st.success("Vocabulary imported successfully!")
                st.json(vocab_data)
            else:
                st.error("Invalid JSON format. Expected {'vocabulary': [...] }")
        except json.JSONDecodeError:
            st.error("Error decoding JSON file. Please check the file format.")
    
    if "imported_vocab" in st.session_state:
        json_str = json.dumps(st.session_state["imported_vocab"], ensure_ascii=False, indent=2)
        st.download_button(
            label="Export Imported JSON",
            data=json_str,
            file_name="imported_japanese_vocab.json",
            mime="application/json",
            key="export_imported_btn"
        )

elif page == "Speech to Text":
    st.subheader("Speech to Text")
    st.write("Upload an audio file to convert speech to text")
    audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'], key="audio_file")
    
    if audio_file:
        if st.button("Convert Speech to Text"):
            with st.spinner("Converting speech to text..."):
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    text = speech_to_text(tmp_file.name)
                    st.success("Conversion complete!")
                    st.text_area("Transcribed Text", text, height=150)
                os.unlink(tmp_file.name)

elif page == "YouTube Transcript":
    st.subheader("YouTube Transcript Downloader")
    video_url = st.text_input("Enter YouTube Video URL", key="youtube_url")
    
    if video_url:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get Transcript"):
                with st.spinner("Fetching transcript..."):
                    transcript = get_youtube_transcript(video_url)
                    st.session_state["transcript"] = transcript
                    st.success("Transcript retrieved successfully!")
                    st.text_area("Video Transcript", transcript, height=200)
                    
                    # Add download button for transcript
                    st.download_button(
                        label="Download Transcript",
                        data=transcript,
                        file_name="youtube_transcript.txt",
                        mime="text/plain"
                    )
        
        with col2:
            if "transcript" in st.session_state and st.button("Generate Dialogues and Questions"):
                with st.spinner("Generating dialogues and questions... This may take up to 2 minutes."):
                    generated_content = generate_dialogues_and_questions(st.session_state["transcript"])
                    if generated_content.startswith("Error:"):
                        st.error(generated_content)
                    else:
                        st.session_state["generated_content"] = generated_content
                        st.success("Content generated successfully!")
    
    # Display generated content if available
    if "generated_content" in st.session_state:
        # Split the content into dialogue and questions sections
        sections = st.session_state["generated_content"].split("\n\n")
        
        # Display dialogue in an expander
        with st.expander("Generated Dialogue", expanded=True):
            st.markdown(sections[0].replace("DIALOGUE:", "").strip())
        
        # Display questions in an expander
        with st.expander("Comprehension Questions", expanded=True):
            st.markdown("\n".join(sections[1:]).replace("QUESTIONS:", "").strip())
        
        # Add download button for generated content
        st.download_button(
            label="Download Generated Content",
            data=st.session_state["generated_content"],
            file_name="generated_content.txt",
            mime="text/plain"
        )

elif page == "Text to Speech":
    st.subheader("Text to Speech")
    tts_text = st.text_area("Enter text to convert to speech", key="tts_input")
    language = st.selectbox("Select Language", ["ja", "en"], key="tts_language")
    
    if tts_text and st.button("Convert to Speech"):
        with st.spinner("Converting text to speech..."):
            try:
                audio_file = text_to_speech(tts_text, language)
                
                # Read the audio file and create a download button
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label="Download Audio",
                        data=audio_bytes,
                        file_name="speech.mp3",
                        mime="audio/mp3"
                    )
                
                # Clean up the temporary file
                os.unlink(audio_file)
            except Exception as e:
                st.error(f"Error generating speech: {str(e)}")

# Footer
st.write("---")
st.write("Built with Streamlit and Mistral (Ollama) - For internal use only.")