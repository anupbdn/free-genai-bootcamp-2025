import base64
from io import BytesIO
from gtts import gTTS
import os
import tempfile
import streamlit as st

# Optional: Import Google Cloud TTS
try:
    import google.cloud.texttospeech as tts
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

def generate_audio_google_cloud(text, language='en-US', voice_name=None, voice_gender='NEUTRAL', 
                               voice_type='Standard', speaking_rate=1.0, pitch=0.0, credentials_path=None):
    """Generate audio using Google Cloud Text-to-Speech"""
    try:
        # Initialize the client with credentials if provided
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = tts.TextToSpeechClient(credentials=credentials)
        else:
            # Try to use default credentials
            client = tts.TextToSpeechClient()
        
        # Set the text input to be synthesized
        synthesis_input = tts.SynthesisInput(text=text)
        
        # Map language codes from gTTS format to Google Cloud format if needed
        language_map = {
            'ja': 'ja-JP',
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'ko': 'ko-KR',
            'zh-cn': 'cmn-CN',
            'ru': 'ru-RU',
            'pt': 'pt-PT',
            'nl': 'nl-NL',
            'pl': 'pl-PL'
        }
        
        cloud_language = language_map.get(language, language)
        
        # Build the voice request
        if voice_name:
            voice = tts.VoiceSelectionParams(
                name=voice_name,
                language_code=cloud_language
            )
        else:
            voice = tts.VoiceSelectionParams(
                language_code=cloud_language,
                ssml_gender=getattr(tts.SsmlVoiceGender, voice_gender)
            )
        
        # Select the type of audio file
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Return the audio content
        return response.audio_content
    except Exception as e:
        st.error(f"Error generating audio with Google Cloud TTS: {str(e)}")
        # Fall back to gTTS
        st.warning("Falling back to gTTS...")
        return generate_audio_gtts(text, language.split('-')[0] if '-' in language else language)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def list_google_cloud_voices(language_code=None, credentials_path=None):
    """List available voices from Google Cloud Text-to-Speech"""
    if not GOOGLE_CLOUD_AVAILABLE:
        return []
        
    try:
        # Initialize the client with credentials if provided
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = tts.TextToSpeechClient(credentials=credentials)
        else:
            # Try to use default credentials
            client = tts.TextToSpeechClient()
        
        # List all available voices
        response = client.list_voices(language_code=language_code)
        voices = []
        
        for voice in response.voices:
            # Get voice details
            name = voice.name
            gender = tts.SsmlVoiceGender(voice.ssml_gender).name
            languages = voice.language_codes
            
            # Determine voice type (Standard, WaveNet, Neural2, Studio)
            voice_type = "Standard"
            if "Neural2" in name:
                voice_type = "Neural2"
            elif "Studio" in name:
                voice_type = "Studio"
            elif "Wavenet" in name:
                voice_type = "WaveNet"
            
            # Add to list
            voices.append({
                "name": name,
                "gender": gender,
                "languages": languages,
                "type": voice_type
            })
        
        return voices
    except Exception as e:
        st.error(f"Error listing voices: {str(e)}")
        return []

def generate_audio_gtts(text, language='en', slow=False):
    """Generate audio using gTTS (Google Translate TTS)"""
    try:
        tts_engine = gTTS(text=text, lang=language, slow=slow)
        fp = BytesIO()
        tts_engine.write_to_fp(fp)
        audio_data = fp.getvalue()
        
        # Verify audio data isn't too small (would indicate an error)
        if len(audio_data) < 100:
            # Try again with English if the language wasn't supported
            tts_engine = gTTS(text=text, lang='en', slow=slow)
            fp = BytesIO()
            tts_engine.write_to_fp(fp)
            audio_data = fp.getvalue()
        
        return audio_data
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return generate_beep_sound()

def generate_beep_sound():
    """Generate a simple beep/fallback sound"""
    # Return a small valid MP3 file (1 second of silence)
    return b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def get_audio_player(audio_bytes):
    """Create an HTML audio player for the audio content"""
    if not audio_bytes or len(audio_bytes) < 100:
        audio_bytes = generate_beep_sound()
    
    b64 = base64.b64encode(audio_bytes).decode()
    audio_player = f'<audio controls><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    return audio_player

@st.cache_data(ttl=3600)  # Cache for 1 hour to avoid regenerating the same audio
def text_to_speech(text, language='en', slow=False, engine='gtts', voice_options=None):
    """Convert text to speech and return audio bytes
    
    Args:
        text: The text to convert to speech
        language: The language code (e.g., 'en', 'ja', 'fr')
        slow: Whether to use slower speech rate (only for gTTS)
        engine: The TTS engine to use ('gtts' or 'google_cloud')
        voice_options: Options for Google Cloud TTS (dict with voice_name, voice_gender, voice_type, etc.)
    
    Returns:
        Audio bytes for the generated speech
    """
    if engine == 'google_cloud' and GOOGLE_CLOUD_AVAILABLE:
        # Set default options
        options = {
            'voice_gender': 'NEUTRAL',
            'voice_type': 'Standard',
            'speaking_rate': 1.0 if not slow else 0.75,
            'pitch': 0.0,
            'credentials_path': None
        }
        
        # Update with provided options
        if voice_options:
            options.update(voice_options)
            
        return generate_audio_google_cloud(
            text=text, 
            language=language, 
            voice_name=voice_options.get('voice_name') if voice_options else None,
            voice_gender=options['voice_gender'],
            voice_type=options['voice_type'],
            speaking_rate=options['speaking_rate'],
            pitch=options['pitch'],
            credentials_path=options['credentials_path']
        )
    else:
        # Use gTTS
        return generate_audio_gtts(text, language, slow)

def save_google_cloud_credentials(credentials_json):
    """Save Google Cloud credentials from a JSON file upload to a temporary file
    
    Args:
        credentials_json: The JSON file uploaded through Streamlit
        
    Returns:
        str: Path to the saved credentials file
    """
    try:
        # Save the credentials file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            tmp_file.write(credentials_json.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving credentials: {str(e)}")
        return None 