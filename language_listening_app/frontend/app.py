import streamlit as st
from streamlit_option_menu import option_menu
import os
import sys
import uuid
import json
from dotenv import load_dotenv
from datetime import datetime

# Add the root directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

# Import components - use absolute imports with the parent directory in sys.path
from backend.app_service import AppService
from models.schemas import Question, QuestionSet
from utils.tts_utils import text_to_speech, get_audio_player
# from language_listening_app.backend.app_service import AppService
# from language_listening_app.models.schemas import Question, QuestionSet
# from language_listening_app.backend.app_service import AppService

# Initialize app service
app_service = AppService()

# Functions for saving and loading question history
def save_question_history(question_set):
    """Save a question set to the history JSON file"""
    history_file = os.path.join(parent_dir, 'data', 'question_history.json')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Convert question set to dict and add timestamp
    question_data = {
        'id': question_set.id,
        'transcript_id': question_set.transcript_id,
        'url': question_set.metadata.get('url', ''),
        'language': question_set.metadata.get('language', 'en'),
        'timestamp': datetime.now().isoformat(),
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'answer': q.answer,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'question_type': q.question_type
            }
            for q in question_set.questions
        ]
    }
    
    # Add to history (at the beginning)
    history.insert(0, question_data)
    
    # Keep only the last 20 items
    history = history[:20]
    
    # Save back to file
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

def load_question_history():
    """Load question history from the JSON file"""
    history_file = os.path.join(parent_dir, 'data', 'question_history.json')
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except:
        return []

# Set page config
st.set_page_config(
    page_title="Language Listening Comprehension",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .info-text {
        font-size: 1rem;
        color: #616161;
    }
    .success-box {
        padding: 1rem;
        background-color: #E8F5E9;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #4CAF50;
        margin: 1rem 0;
    }
    .question-box {
        padding: 1.5rem;
        background-color: #E3F2FD;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 0.5rem solid #2196F3;
    }
    .answer-box {
        padding: 1rem;
        background-color: #E1F5FE;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 0.5rem solid #0288D1;
    }
    .explanation-box {
        padding: 1rem;
        background-color: #FFFDE7;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 0.5rem solid #FDD835;
    }
    /* Make expander content more visible */
    .st-emotion-cache-1kyxreq {
        background-color: #F8F9FA;
        padding: 10px;
        border-radius: 5px;
    }
    /* Make text darker for better contrast */
    p {
        color: #212121;
    }
    h4 {
        color: #0D47A1;
    }
    /* Audio section styling */
    .audio-section {
        background-color: #F5F5F5;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #2196F3;
    }
    /* Audio button styling */
    .st-emotion-cache-1erivem {
        border-color: #2196F3;
        color: #2196F3;
    }
    .st-emotion-cache-1erivem:hover {
        border-color: #0D47A1;
        color: #0D47A1;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Language Listening Comprehension</h1>", unsafe_allow_html=True)
st.markdown("<p class='info-text'>Improve your language listening skills with AI-generated comprehension questions from YouTube videos.</p>", unsafe_allow_html=True)

# Main app
def main():
    # Initialize session state variables if they don't exist
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = ""
    if 'question_history' not in st.session_state:
        st.session_state.question_history = load_question_history()
    if 'provider' not in st.session_state:
        st.session_state.provider = "ollama"
    if 'model' not in st.session_state:
        st.session_state.model = "mistral:latest"
    # Score-related variables
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_answered' not in st.session_state:
        st.session_state.total_answered = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'question_results' not in st.session_state:
        st.session_state.question_results = []  # List to track results for each question
    # TTS-related variables
    if 'tts_slow' not in st.session_state:
        st.session_state.tts_slow = False
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = "gtts"  # Default to gTTS
    if 'google_credentials_path' not in st.session_state:
        st.session_state.google_credentials_path = None
    if 'google_voice_gender' not in st.session_state:
        st.session_state.google_voice_gender = "NEUTRAL"
    if 'google_voice_type' not in st.session_state:
        st.session_state.google_voice_type = "Standard"
    if 'google_voice_name' not in st.session_state:
        st.session_state.google_voice_name = None
    if 'google_speaking_rate' not in st.session_state:
        st.session_state.google_speaking_rate = 1.0
    if 'google_pitch' not in st.session_state:
        st.session_state.google_pitch = 0.0
    if 'available_voices' not in st.session_state:
        st.session_state.available_voices = []

    # Sidebar
    with st.sidebar:
        selected = option_menu(
            "Language Listening App",
            ["Home", "Interactive Learning", "History"],
            icons=["house", "book", "clock-history"],
            menu_icon="translate",
            default_index=["Home", "Interactive Learning", "History"].index(st.session_state.current_page),
        )
        st.session_state.current_page = selected
        
        # Add model selection options
        st.sidebar.markdown("---")
        st.sidebar.header("Model Settings")
        
        # LLM provider selection
        provider = st.sidebar.radio(
            "Select LLM Provider",
            options=["ollama", "bedrock"],
            format_func=lambda x: "Ollama (Local)" if x == "ollama" else "Amazon Bedrock (Cloud)",
            index=0 if st.session_state.provider == "ollama" else 1
        )
        st.session_state.provider = provider
        
        # Model selection based on provider
        if provider == "ollama":
            model = st.sidebar.selectbox(
                "Select Ollama Model",
                options=["mistral:latest", "llama2:latest", "gemma:latest"],
                index=["mistral:latest", "llama2:latest", "gemma:latest"].index(st.session_state.model) 
                if st.session_state.model in ["mistral:latest", "llama2:latest", "gemma:latest"] else 0
            )
        else:
            model = st.sidebar.selectbox(
                "Select Bedrock Model",
                options=["amazon.nova-micro-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"],
                index=["amazon.nova-micro-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"].index(st.session_state.model)
                if st.session_state.model in ["amazon.nova-micro-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"] else 0
            )
        st.session_state.model = model
        
        # Number of questions
        num_questions = st.sidebar.slider("Number of Questions", min_value=3, max_value=20, value=10)
        st.session_state.num_questions = num_questions
        
        # Add Text-to-Speech settings
        st.sidebar.markdown("---")
        st.sidebar.header("Audio Settings")
        
        # TTS engine selection
        tts_engine = st.sidebar.radio(
            "Text-to-Speech Engine",
            options=["gtts", "google_cloud"],
            format_func=lambda x: "gTTS (Basic)" if x == "gtts" else "Google Cloud TTS (Advanced)",
            index=0 if st.session_state.tts_engine == "gtts" else 1,
            help="Select the text-to-speech engine. Google Cloud TTS offers better quality voices but requires credentials."
        )
        st.session_state.tts_engine = tts_engine
        
        # Slower speech option for gTTS
        if tts_engine == "gtts":
            tts_slow = st.sidebar.checkbox("Slower Speech Rate", value=st.session_state.tts_slow,
                                         help="Use a slower speech rate for better comprehension")
            st.session_state.tts_slow = tts_slow
        
        # Google Cloud TTS settings
        elif tts_engine == "google_cloud":
            from utils.tts_utils import GOOGLE_CLOUD_AVAILABLE, save_google_cloud_credentials
            
            if not GOOGLE_CLOUD_AVAILABLE:
                st.sidebar.error("Google Cloud Text-to-Speech is not available. Please install the package: pip install google-cloud-texttospeech")
            else:
                # Credentials file uploader
                st.sidebar.subheader("Google Cloud Credentials")
                credentials_file = st.sidebar.file_uploader(
                    "Upload Google Cloud credentials JSON file",
                    type=["json"],
                    help="Upload your Google Cloud service account credentials JSON file for Text-to-Speech."
                )
                
                if credentials_file is not None:
                    # Save the credentials file
                    credentials_path = save_google_cloud_credentials(credentials_file)
                    if credentials_path:
                        st.session_state.google_credentials_path = credentials_path
                        st.sidebar.success("Credentials uploaded successfully!")
                
                # Voice settings
                st.sidebar.subheader("Voice Settings")
                
                # Voice gender
                voice_gender = st.sidebar.selectbox(
                    "Voice Gender",
                    options=["NEUTRAL", "MALE", "FEMALE"],
                    index=["NEUTRAL", "MALE", "FEMALE"].index(st.session_state.google_voice_gender),
                    help="Select the gender of the voice."
                )
                st.session_state.google_voice_gender = voice_gender
                
                # Voice type
                voice_type = st.sidebar.selectbox(
                    "Voice Quality",
                    options=["Standard", "WaveNet", "Neural2", "Studio"],
                    index=["Standard", "WaveNet", "Neural2", "Studio"].index(st.session_state.google_voice_type)
                    if st.session_state.google_voice_type in ["Standard", "WaveNet", "Neural2", "Studio"] else 0,
                    help="Standard is basic. WaveNet, Neural2, and Studio offer progressively higher quality voices."
                )
                st.session_state.google_voice_type = voice_type
                
                # Speaking rate 
                speaking_rate = st.sidebar.slider(
                    "Speaking Rate", 
                    min_value=0.5, 
                    max_value=2.0, 
                    value=st.session_state.google_speaking_rate,
                    step=0.05,
                    help="1.0 is normal speed. Lower values slow down speech, higher values speed it up."
                )
                st.session_state.google_speaking_rate = speaking_rate
                
                # Pitch
                pitch = st.sidebar.slider(
                    "Pitch",
                    min_value=-10.0,
                    max_value=10.0,
                    value=st.session_state.google_pitch,
                    step=1.0,
                    help="0 is normal pitch. Negative values lower the pitch, positive values raise it."
                )
                st.session_state.google_pitch = pitch
        
        # Display question history in sidebar
        st.sidebar.markdown("---")
        st.sidebar.header("Question History")
        
        if not st.session_state.question_history:
            st.sidebar.info("No question history yet. Generate questions in Interactive Learning to see them here.")
        else:
            for i, question_set in enumerate(st.session_state.question_history[:5]):  # Show only the 5 most recent
                with st.sidebar.expander(f"Questions from {question_set.get('timestamp', '').split('T')[0]} ({question_set.get('language', 'en')})"):
                    for j, q in enumerate(question_set.get('questions', [])):
                        st.markdown(f"**Q{j+1}:** {q.get('text', '')}")
                        if st.button(f"View Details #{i}-{j}", key=f"view_q_{i}_{j}"):
                            # Set up session state to view this question set in Interactive Learning
                            st.session_state.current_page = "Interactive Learning"
                            # We would need to reconstruct the transcript and questions here
                            # This is a placeholder for that functionality
                            st.rerun()

    # Main content
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Interactive Learning":
        interactive_learning_page()
    elif st.session_state.current_page == "History":
        history_page()

def home_page():
    st.title("Language Listening App")
    st.markdown("### Welcome to the Language Listening App!")
    st.markdown("""
    This application helps you improve your language listening skills by:
    
    1. **Processing YouTube videos** in various languages
    2. **Generating comprehension questions in the target language** based on the content
    3. **Testing your understanding** through interactive exercises
    4. **Tracking your progress** with a history of previous questions
    
    To get started, navigate to the **Interactive Learning** section and enter a YouTube URL.
    """)
    
    # Add feature highlight
    st.markdown("### Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Multi-language Support")
        st.markdown("""
        Practice listening comprehension in multiple languages:
        - Japanese 🇯🇵
        - Korean 🇰🇷
        - Chinese 🇨🇳
        - Spanish 🇪🇸
        - French 🇫🇷
        - German 🇩🇪
        - And more!
        """)
    
    with col2:
        st.markdown("#### 🧠 Immersive Learning")
        st.markdown("""
        - Questions generated in the target language
        - Self-evaluation to track your progress
        - Explanations provided in English for clarity
        - Practice with real-world content from YouTube
        - **NEW:** Text-to-speech with natural voices
        """)
    
    # Display app settings
    st.markdown("### App Settings")
    
    # Language selection
    with st.expander("Language Settings"):
        st.selectbox(
            "Default Language",
            options=["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "zh-cn", "ko"],
            format_func=lambda x: {
                "en": "English 🇺🇸", 
                "es": "Spanish 🇪🇸",
                "fr": "French 🇫🇷",
                "de": "German 🇩🇪",
                "it": "Italian 🇮🇹",
                "pt": "Portuguese 🇵🇹",
                "nl": "Dutch 🇳🇱",
                "pl": "Polish 🇵🇱",
                "ru": "Russian 🇷🇺",
                "ja": "Japanese 🇯🇵", 
                "ko": "Korean 🇰🇷", 
                "zh-cn": "Chinese (Simplified) 🇨🇳"
            }.get(x, x),
            key="default_language"
        )
    
    # TTS Settings
    with st.expander("Text-to-Speech Settings"):
        st.markdown("""
        This app supports two TTS engines:
        1. **gTTS (Basic)**: Simple Google Translate voices, no setup required
        2. **Google Cloud TTS (Advanced)**: Higher quality voices with more options, requires credentials
        
        You can change the TTS engine in the sidebar under "Audio Settings".
        """)
        
        # Google Cloud credentials setup
        st.markdown("#### Google Cloud TTS Setup")
        st.markdown("""
        To use Google Cloud TTS, you need a Google Cloud account with Text-to-Speech API enabled. 
        You can follow these steps:
        
        1. Create a Google Cloud account or sign in to your existing one
        2. Create a new project
        3. Enable the Text-to-Speech API
        4. Create a service account key and download the JSON file
        5. Upload the JSON file in the sidebar under "Audio Settings"
        
        **Demo credentials:** For testing purposes, you can use example credentials below. 
        Note that these demo credentials may have usage limitations.
        """)
        
        # Show example credentials for easy copy-paste
        example_credentials = """{
    "type": "service_account",
    "project_id": "playground-s-11-2cfe7aab",
    "private_key_id": "3e2aee350fbbca68b076bb89929ea20a05ee2d47",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCd6EH03QguKgRc\\nYT+Yif7MccFgFwbbahltcbsmNEBOreDUyZoHzWmtNXjElbl3ChWohZOwDJQ3sz+7\\n8uYPoxMRRNgyqwe5wLsb6uY5qrxgjVfchbPpOt4N3cV/JflEkzJk/3nVlFgiWhlH\\nQ2uypmiDN4JWhgJqZVRik8idoQZc5pI8Yt+oAbVn47SBljc3dBsgJ0sgB0GxNAHu\\nD6K2zEa4fhRwdZ1vTOLp+1iY+GB4UhujQkL0e5n2fNJ0tojgVQKmlcpjVds7cCpy\\nd2qSM9nE1NsYQBJipNloyp1y8I7aaFGBO1F21sSQVYO9JJw0CmcBdg7Xh1d48BdO\\nAkhGZ4QHAgMBAAECggEARaX8dY8KfSYuPzrrrJHtT2q7YvE1JpFBPutDo2G3nZyH\\nBwQXCur4+huUNY1evRk3HVoxnpylwX2wFmvYOrxwfBT0EUEryqwuO22b94KNzT56\\nqvtUNAKxj8cqRd9Pd4Y/W5ntuJ1SVHCOJscfmTBZ98qDlDtOlHQ2SLarbY9pOY8O\\nJfU/ljwE0IcLjv818m4Y961rURDuaFwRHEtPdc982gbDj8MFZOY9k3UL0ytPQMHN\\nM0A1IJA6oP4iA18V8KyWhn/twjky1n07EwVuhfYZCnaGRYlTkvy7BbdeC+k6e65f\\n8iPDkDslGIVyG7nt2HLTxgF28JpdrkOO1TCedjpdBQKBgQDQYXsGe+ZUCNawfUJw\\nJu8dto4TwFYDIICy3Ye/jqY46lFy0niDceRR9IcXNuWcP9TFyib0QLe9+vx7Z1Cq\\nrCEAst2dOci2ZvWO1UiV3fFuRz8NK/f5ogZMrKtKFYtQLZ1VgWkRYGHyaHea2Lx5\\nqKBUzxizupi5J47NvgiaSoCARQKBgQDB/gRI9YVtghrMrKz34NnWSJxCKSQJtG0j\\nMmkh04Px/hbm6WpqeIMU7UP6Y++zh9p4qBtBYDDisqX963AsfEdSM39RVXglOhNy\\nUexkR+Pl9ipVQw/j5W1btS4c8iCjIqkYYPC2srLtFxfK1TxijazxG3TGxabyllu/\\nOjDUc7W12wKBgQCJ6VowymOADnF4UQ5dh4cN1Tpm3A6Q9zv2JSOopdJhLMNHCQD1\\njbUcgIe/13dTV/OMC+SIFyUEOU5Mpe3/ZvhYrAh7/DhYb//ozkPB3CfjYofaQdVW\\ng+NDb6vV1jhjkizk4EcXVwC8HGO8OeFTa0ThnEau/LoDIKkkhbbP1qsBOQKBgQCC\\nyVbqOV0zbzvSMbiLhbRXm6x9jm8Ve+b4i8wFWiziwYN/Om7cSVNWkH/8F9RLHZRV\\nNEDr2oYa0IbIoiqGU2NiMAXuN8lAj978e+77zNwA9e2kfgoAg3UvFv931GXclkma\\nfgDLq76lyaPow8pqR0oJY5FfUXI0qtpAGmNBWKFxcQKBgHtp1YVaYAO7K4zHhRvE\\nCqZ3jtKp2G2H+J30W+KnB5Y1LcWb+gAIYmw6KCRQsNqwjNF5zclwRA6B9s0u0Ueh\\nnH6tJHXpjbv8KU3KqdSEHdb2IrVZuK9UPbFB2FoSFr6zs4CPa6BxLn0aWalzR0mU\\nipso6tlfWkP2e6Rp5r0t52bC\\n-----END PRIVATE KEY-----\\n",
    "client_email": "cli-service-account-1@playground-s-11-2cfe7aab.iam.gserviceaccount.com",
    "client_id": "112330951363357575411",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cli-service-account-1%40playground-s-11-2cfe7aab.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}"""
        
        st.code(example_credentials, language="json")
        
        # Instructions on how to use the credentials
        st.markdown("""
        To use these credentials:
        1. Copy the JSON above
        2. Create a new file in any text editor and paste the JSON
        3. Save the file as `google_cloud_credentials.json`
        4. Upload the file in the sidebar under "Audio Settings"
        """)
    
    # Quick start button
    if st.button("Go to Interactive Learning"):
        st.session_state.current_page = "Interactive Learning"
        st.rerun()

def history_page():
    st.title("History")
    st.markdown("View your previously processed videos and generated questions.")
    
    # Get all transcripts from vector store
    try:
        from backend.vector_store import VectorStoreManager
        vector_store = VectorStoreManager()
        all_transcripts = vector_store.get_all_transcripts()
        
        # Display transcripts from vector store
        if all_transcripts:
            st.markdown("### Processed Videos")
            st.markdown(f"Found {len(all_transcripts)} processed videos in the database.")
            
            for i, transcript in enumerate(all_transcripts, 1):
                try:
                    # Get a display title for the transcript
                    display_title = transcript.url if hasattr(transcript, 'url') and transcript.url else f"Transcript {transcript.video_id}"
                    
                    with st.expander(f"Video {i}: {display_title}"):
                        if hasattr(transcript, 'url') and transcript.url:
                            st.markdown(f"**URL:** {transcript.url}")
                        st.markdown(f"**Language:** {transcript.language}")
                        st.markdown(f"**ID:** {transcript.video_id}")
                        st.markdown(f"**Chunks:** {len(transcript.chunks)}")
                        
                        # Get questions for this transcript
                        try:
                            questions = vector_store.get_questions_for_transcript(transcript.video_id)
                            
                            if questions:
                                st.markdown(f"**Questions:** {len(questions)}")
                                
                                # Display a few sample questions
                                st.markdown("### Sample Questions:")
                                for j, question in enumerate(questions[:3], 1):
                                    # Create columns for question text and listen button
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**Question {j}:** {question.text}")
                                    with col2:
                                        # Add audio button for question
                                        if st.button(f"🔊 Listen", key=f"listen_vq_{i}_{j}"):
                                            voice_options = get_voice_options()
                                            audio_bytes = text_to_speech(
                                                question.text, 
                                                transcript.language, 
                                                st.session_state.get('tts_slow', False),
                                                st.session_state.get('tts_engine', 'gtts'),
                                                voice_options
                                            )
                                            st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
                                    
                                    # Create columns for answer
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**Answer:** {question.answer}")
                                    with col2:
                                        # Add audio button for answer
                                        if st.button(f"🔊 Listen", key=f"listen_va_{i}_{j}"):
                                            voice_options = get_voice_options()
                                            audio_bytes = text_to_speech(
                                                question.answer, 
                                                transcript.language, 
                                                st.session_state.get('tts_slow', False),
                                                st.session_state.get('tts_engine', 'gtts'),
                                                voice_options
                                            )
                                            st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
                                    
                                    st.markdown("---")
                                
                                # Button to practice with this question set
                                if st.button(f"Practice with this video #{i}", key=f"practice_{i}"):
                                    # Create a question set and store in session state
                                    metadata = {'language': transcript.language}
                                    if hasattr(transcript, 'url') and transcript.url:
                                        metadata['url'] = transcript.url
                                    
                                    question_set = QuestionSet(
                                        id=str(uuid.uuid4()),
                                        transcript_id=transcript.video_id,
                                        questions=questions,
                                        metadata=metadata
                                    )
                                    
                                    # Store in session state
                                    st.session_state.transcript = transcript
                                    st.session_state.questions = question_set.questions
                                    st.session_state.current_question_index = 0
                                    st.session_state.show_answer = False
                                    st.session_state.user_answer = ""
                                    
                                    # Reset score
                                    st.session_state.score = 0
                                    st.session_state.total_answered = 0
                                    st.session_state.correct_answers = 0
                                    st.session_state.question_results = []
                                    
                                    # Navigate to Interactive Learning
                                    st.session_state.current_page = "Interactive Learning"
                                    st.rerun()
                            else:
                                st.markdown("No questions found for this transcript.")
                        except Exception as e:
                            st.error(f"Error getting questions for transcript: {str(e)}")
                except Exception as e:
                    st.error(f"Error displaying transcript {i}: {str(e)}")
                    continue
        else:
            st.info("No processed videos found in the database.")
    except Exception as e:
        st.error(f"Error accessing vector store: {str(e)}")
    
    # Display saved question history
    st.markdown("### Question History")
    st.markdown("Questions you've generated in previous sessions:")
    
    if not st.session_state.question_history:
        st.info("No question history found. Generate questions in Interactive Learning to see them here.")
    else:
        for i, question_set in enumerate(st.session_state.question_history):
            timestamp = question_set.get('timestamp', '').split('T')[0]
            language = question_set.get('language', 'en')
            url = question_set.get('url', '')
            
            with st.expander(f"Question Set {i+1} - {timestamp} ({language})"):
                if url:
                    st.markdown(f"**Source:** {url}")
                
                st.markdown(f"**Language:** {language}")
                st.markdown(f"**Generated on:** {timestamp}")
                
                # Display questions
                for j, q in enumerate(question_set.get('questions', [])):
                    # Create columns for question text and listen button
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Question {j+1}:** {q.get('text', '')}")
                    with col2:
                        # Add audio button for question
                        if st.button(f"🔊 Listen", key=f"listen_q_{i}_{j}"):
                            voice_options = get_voice_options()
                            audio_bytes = text_to_speech(
                                q.get('text', ''), 
                                language, 
                                st.session_state.get('tts_slow', False),
                                st.session_state.get('tts_engine', 'gtts'),
                                voice_options
                            )
                            st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
                    
                    # Use a button to show answer instead of nested expander
                    answer_key = f"show_answer_{i}_{j}"
                    if answer_key not in st.session_state:
                        st.session_state[answer_key] = False
                    
                    if st.button(f"Show Answer #{j+1}", key=f"btn_answer_{i}_{j}"):
                        st.session_state[answer_key] = not st.session_state[answer_key]
                    
                    if st.session_state[answer_key]:
                        # Create columns for answer
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**Answer:** {q.get('answer', '')}")
                        with col2:
                            # Add audio button for answer
                            if st.button(f"🔊 Listen", key=f"listen_a_{i}_{j}"):
                                voice_options = get_voice_options()
                                audio_bytes = text_to_speech(
                                    q.get('answer', ''), 
                                    language, 
                                    st.session_state.get('tts_slow', False),
                                    st.session_state.get('tts_engine', 'gtts'),
                                    voice_options
                                )
                                st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
                        
                        if 'explanation' in q:
                            st.markdown(f"**Explanation:** {q.get('explanation', '')}")
                        if 'difficulty' in q:
                            st.markdown(f"**Difficulty:** {q.get('difficulty', '')}")
                    
                    st.markdown("---")
                
                # Button to practice with this question set
                if st.button(f"Practice with this set #{i+1}", key=f"practice_history_{i}"):
                    # Reconstruct questions for practice
                    from models.schemas import Question
                    
                    questions = [
                        Question(
                            id=q.get('id', str(uuid.uuid4())),
                            text=q.get('text', ''),
                            answer=q.get('answer', ''),
                            explanation=q.get('explanation', ''),
                            difficulty=q.get('difficulty', 'medium'),
                            context='',
                            question_type=q.get('question_type', 'comprehension')
                        )
                        for q in question_set.get('questions', [])
                    ]
                    
                    # Store in session state
                    st.session_state.questions = questions
                    st.session_state.current_question_index = 0
                    st.session_state.show_answer = False
                    st.session_state.user_answer = ""
                    
                    # Reset score
                    st.session_state.score = 0
                    st.session_state.total_answered = 0
                    st.session_state.correct_answers = 0
                    st.session_state.question_results = []
                    
                    # Navigate to Interactive Learning
                    st.session_state.current_page = "Interactive Learning"
                    st.rerun()

def interactive_learning_page():
    st.title("Interactive Learning")
    
    # URL input
    url = st.text_input("Enter YouTube URL", key="url_input")
    
    # Language selection with more descriptive label
    language = st.selectbox(
        "Select Target Language (questions will be generated in this language)",
        ["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "zh-cn", "ko"],
        format_func=lambda x: {
            "en": "English 🇺🇸", 
            "es": "Spanish 🇪🇸",
            "fr": "French 🇫🇷",
            "de": "German 🇩🇪",
            "it": "Italian 🇮🇹",
            "pt": "Portuguese 🇵🇹",
            "nl": "Dutch 🇳🇱",
            "pl": "Polish 🇵🇱",
            "ru": "Russian 🇷🇺",
            "ja": "Japanese 🇯🇵", 
            "ko": "Korean 🇰🇷", 
            "zh-cn": "Chinese (Simplified) 🇨🇳"
        }.get(x, x),
        key="language_select"
    )
    
    # Add info about language
    if language != "en":
        st.info(f"Questions will be generated in {language} language to help you practice your listening comprehension. Explanations will be provided in English to help you understand.")
    
    # Process button
    if st.button("Process Video", key="process_button"):
        with st.spinner("Processing video..."):
            try:
                # Get transcript
                transcript = app_service.get_transcript(url, language)
                
                # Store in session state
                st.session_state.transcript = transcript
                
                # Generate questions
                metadata = {"language": language}
                if hasattr(transcript, 'url') and transcript.url:
                    metadata["url"] = transcript.url
                
                # Use the selected provider and model
                question_set = app_service.generate_questions(
                    transcript, 
                    provider=st.session_state.provider,
                    model=st.session_state.model,
                    metadata=metadata,
                    num_questions=st.session_state.num_questions
                )
                
                # Store in session state
                st.session_state.questions = question_set.questions
                st.session_state.current_question_index = 0
                st.session_state.show_answer = False
                st.session_state.user_answer = ""
                
                # Reset score
                st.session_state.score = 0
                st.session_state.total_answered = 0
                st.session_state.correct_answers = 0
                st.session_state.question_results = []
                
                # Save to question history
                save_question_history(question_set)
                st.session_state.question_history = load_question_history()
                
                st.success("Questions generated successfully!")
                
            except Exception as e:
                error_message = str(e)
                if "UnrecognizedClientException" in error_message or "security token" in error_message:
                    st.error("AWS Authentication Error: The AWS credentials for Bedrock are invalid or expired.")
                    st.markdown("""
                    ### How to fix this:
                    1. You need valid AWS credentials with Bedrock access permissions
                    2. Update the `.env` file with your valid AWS credentials:
                       - AWS_ACCESS_KEY_ID
                       - AWS_SECRET_ACCESS_KEY
                       - AWS_REGION
                    3. Make sure your AWS account has Bedrock enabled and the selected model is available in your region
                    
                    For now, try using the Ollama provider instead.
                    """)
                else:
                    st.error(f"Error: {str(e)}")
    
    # Display questions if available
    if st.session_state.questions:
        display_questions()

def display_questions():
    # Get current question
    if not st.session_state.questions:
        st.warning("No questions available. Please process a video first.")
        return
    
    current_index = st.session_state.current_question_index
    questions = st.session_state.questions
    
    # Display score information
    st.sidebar.markdown("---")
    st.sidebar.header("Your Progress")
    if st.session_state.total_answered > 0:
        accuracy = (st.session_state.correct_answers / st.session_state.total_answered) * 100
        st.sidebar.metric("Score", f"{st.session_state.correct_answers}/{st.session_state.total_answered}", f"{accuracy:.1f}%")
    else:
        st.sidebar.metric("Score", "0/0", "0.0%")
    
    # Display question results
    if st.session_state.question_results:
        with st.sidebar.expander("Question Results"):
            for i, result in enumerate(st.session_state.question_results):
                if result == "correct":
                    st.markdown(f"Q{i+1}: ✅ Correct")
                elif result == "partial":
                    st.markdown(f"Q{i+1}: 🟡 Partially Correct")
                elif result == "incorrect":
                    st.markdown(f"Q{i+1}: ❌ Incorrect")
    
    if current_index >= len(questions):
        # All questions completed - show summary
        st.success("🎉 You've completed all questions!")
        
        # Calculate final score
        if st.session_state.total_answered > 0:
            accuracy = (st.session_state.correct_answers / st.session_state.total_answered) * 100
            
            # Display score summary
            st.markdown(f"### Your Final Score")
            st.markdown(f"**Correct Answers:** {st.session_state.correct_answers}/{st.session_state.total_answered}")
            st.markdown(f"**Accuracy:** {accuracy:.1f}%")
            
            # Provide feedback based on score
            if accuracy >= 90:
                st.markdown("**Excellent work!** You have a strong understanding of the content.")
            elif accuracy >= 70:
                st.markdown("**Good job!** You understand most of the content, but there's room for improvement.")
            elif accuracy >= 50:
                st.markdown("**Not bad!** You've grasped some of the key points, but consider reviewing the content again.")
            else:
                st.markdown("**Keep practicing!** This content seems challenging. Consider watching the video again or trying a different one.")
        
        # Button to restart
        if st.button("Start Over"):
            st.session_state.current_question_index = 0
            st.session_state.show_answer = False
            st.session_state.user_answer = ""
            st.session_state.score = 0
            st.session_state.total_answered = 0
            st.session_state.correct_answers = 0
            st.session_state.question_results = []
            st.rerun()
        
        # Button to try a new video
        if st.button("Process New Video"):
            st.session_state.current_page = "Interactive Learning"
            st.session_state.transcript = None
            st.session_state.questions = []
            st.session_state.current_question_index = 0
            st.session_state.show_answer = False
            st.session_state.user_answer = ""
            st.session_state.score = 0
            st.session_state.total_answered = 0
            st.session_state.correct_answers = 0
            st.session_state.question_results = []
            st.rerun()
        
        return
    
    current_question = questions[current_index]
    
    # Display progress
    st.progress((current_index) / len(questions))
    st.markdown(f"**Question {current_index + 1} of {len(questions)}**")
    
    # Display question with audio option
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### {current_question.text}")
    with col2:
        # Get language from session state or use question language if available
        language = None
        if st.session_state.transcript and hasattr(st.session_state.transcript, 'language'):
            language = st.session_state.transcript.language
        else:
            # Try to get from session state
            language = st.session_state.get('language', 'en')
        
        # Add TTS button for question
        if st.button("🔊 Listen to Question", key=f"listen_question_{current_index}"):
            voice_options = get_voice_options()
            audio_bytes = text_to_speech(
                current_question.text, 
                language, 
                st.session_state.get('tts_slow', False),
                st.session_state.get('tts_engine', 'gtts'),
                voice_options
            )
            st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
    
    # User answer input
    user_answer = st.text_area("Your Answer", value=st.session_state.user_answer, height=100)
    st.session_state.user_answer = user_answer
    
    # Check answer button
    if st.button("Check Answer"):
        st.session_state.show_answer = True
    
    # Display answer if button clicked
    if st.session_state.show_answer:
        st.markdown("---")
        
        # Display answer with audio option
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**Correct Answer:** {current_question.answer}")
        with col2:
            # Add TTS button for answer
            if st.button("🔊 Listen to Answer", key=f"listen_answer_{current_index}"):
                voice_options = get_voice_options()
                audio_bytes = text_to_speech(
                    current_question.answer, 
                    language, 
                    st.session_state.get('tts_slow', False),
                    st.session_state.get('tts_engine', 'gtts'),
                    voice_options
                )
                st.markdown(f"<div class='audio-section'>{get_audio_player(audio_bytes)}</div>", unsafe_allow_html=True)
        
        st.markdown(f"**Explanation:** {current_question.explanation}")
        
        # Self-evaluation section
        st.markdown("### How did you do?")
        
        col1, col2, col3 = st.columns(3)
        
        # Define callback functions for scoring
        def score_correct():
            st.session_state.correct_answers += 1
            st.session_state.total_answered += 1
            st.session_state.question_results.append("correct")
            st.session_state.current_question_index += 1
            st.session_state.show_answer = False
            st.session_state.user_answer = ""
        
        def score_partial():
            st.session_state.correct_answers += 0.5
            st.session_state.total_answered += 1
            st.session_state.question_results.append("partial")
            st.session_state.current_question_index += 1
            st.session_state.show_answer = False
            st.session_state.user_answer = ""
        
        def score_incorrect():
            st.session_state.total_answered += 1
            st.session_state.question_results.append("incorrect")
            st.session_state.current_question_index += 1
            st.session_state.show_answer = False
            st.session_state.user_answer = ""
        
        with col1:
            st.button("I got it right! ✅", on_click=score_correct)
        
        with col2:
            st.button("I was close 🟡", on_click=score_partial)
        
        with col3:
            st.button("I was wrong ❌", on_click=score_incorrect)

# Footer
st.markdown("---")
st.markdown("### Need help?")
st.markdown("""
- Make sure the YouTube video has captions/transcripts available
- For best results, use videos with clear speech and good audio quality
- If you encounter errors, try a different video or language
""")

# Create voice options dictionary from session state
def get_voice_options():
    """Create a dictionary of voice options from session state"""
    return {
        'voice_name': st.session_state.get('google_voice_name'),
        'voice_gender': st.session_state.get('google_voice_gender', 'NEUTRAL'),
        'voice_type': st.session_state.get('google_voice_type', 'Standard'),
        'speaking_rate': st.session_state.get('google_speaking_rate', 1.0),
        'pitch': st.session_state.get('google_pitch', 0.0),
        'credentials_path': st.session_state.get('google_credentials_path')
    }

# Main function call
if __name__ == "__main__":
    main() 