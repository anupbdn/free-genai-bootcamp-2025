import streamlit as st
from streamlit_option_menu import option_menu
import os
import sys
import uuid
from dotenv import load_dotenv

# Add the root directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

# Import components - use absolute imports with the parent directory in sys.path
from backend.app_service import AppService
from models.schemas import Question, QuestionSet
# from language_listening_app.backend.app_service import AppService
# from language_listening_app.models.schemas import Question, QuestionSet
# from language_listening_app.backend.app_service import AppService

# Initialize app service
app_service = AppService()

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
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Language Listening Comprehension</h1>", unsafe_allow_html=True)
st.markdown("<p class='info-text'>Improve your language listening skills with AI-generated comprehension questions from YouTube videos.</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/listening--v1.png", width=80)
    st.markdown("## Settings")
    
    # Language selection
    language = st.selectbox(
        "Select Language",
        options=["en", "ja", "ko", "zh", "es", "fr", "de"],
        format_func=lambda x: {
            "en": "English 🇺🇸", 
            "ja": "Japanese 🇯🇵", 
            "ko": "Korean 🇰🇷", 
            "zh": "Chinese 🇨🇳",
            "es": "Spanish 🇪🇸",
            "fr": "French 🇫🇷",
            "de": "German 🇩🇪"
        }[x]
    )
    
    # LLM provider selection
    provider = st.radio(
        "Select LLM Provider",
        options=["ollama", "bedrock"],
        format_func=lambda x: "Ollama (Local)" if x == "ollama" else "Amazon Bedrock (Cloud)"
    )
    
    # Model selection based on provider
    if provider == "ollama":
        model = st.selectbox(
            "Select Ollama Model",
            options=["mistral:latest", "llama2:latest", "gemma:latest"]
        )
    else:
        model = st.selectbox(
            "Select Bedrock Model",
            options=["amazon.nova-micro-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0"]
        )
    
    # Number of questions
    num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses AI to generate comprehension questions from YouTube videos to help you practice your listening skills.")
    st.markdown("Made with ❤️ by GenAI Bootcamp 2025")

# Main navigation
selected = option_menu(
    menu_title=None,
    options=["YouTube Transcript", "Interactive Learning", "History"],
    icons=["youtube", "book", "clock-history"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# YouTube Transcript section
if selected == "YouTube Transcript":
    st.markdown("<h2 class='sub-header'>YouTube Transcript</h2>", unsafe_allow_html=True)
    st.markdown("Enter a YouTube URL to extract the transcript and generate comprehension questions.")
    
    # YouTube URL input
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    # Process button
    if st.button("Process Video", type="primary"):
        if youtube_url:
            with st.spinner("Processing video... This may take a minute or two."):
                try:
                    # Process the video
                    question_set = app_service.process_video(
                        url=youtube_url,
                        language=language,
                        provider=provider,
                        model=model
                    )
                    
                    # Store in session state
                    st.session_state.question_set = question_set
                    
                    # Show success message
                    st.markdown(f"""
                    <div class='success-box'>
                        <h3>✅ Video processed successfully!</h3>
                        <p>Generated {len(question_set.questions)} questions</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display questions
                    st.markdown("<h3>Generated Questions</h3>", unsafe_allow_html=True)
                    
                    for i, question in enumerate(question_set.questions, 1):
                        with st.expander(f"Question {i}: {question.text}"):
                            st.markdown(f"""
                            <div class='answer-box'>
                                <h4>Answer:</h4>
                                <p style="font-weight: 500;">{question.answer}</p>
                            </div>
                            <div class='explanation-box'>
                                <h4>Explanation:</h4>
                                <p style="font-weight: 500;">{question.explanation}</p>
                            </div>
                            <p><strong>Difficulty:</strong> {question.difficulty}</p>
                            """, unsafe_allow_html=True)
                    
                    # Option to start interactive learning
                    st.markdown("---")
                    st.markdown("### Ready to practice?")
                    
                    # Define callback function
                    def go_to_interactive():
                        st.session_state.selected = "Interactive Learning"
                    
                    if st.button("Start Interactive Learning", on_click=go_to_interactive):
                        pass
                
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
                        st.error(f"Error processing video: {error_message}")
                        st.markdown("""
                        **Possible issues:**
                        - The video might not have transcripts available in the selected language
                        - The URL might be invalid
                        - There might be an issue with the LLM provider
                        
                        Try a different video or language.
                        """)
        else:
            st.warning("Please enter a YouTube URL")

# Interactive Learning section
elif selected == "Interactive Learning":
    st.markdown("<h2 class='sub-header'>Interactive Learning</h2>", unsafe_allow_html=True)
    
    # Check if we have questions in session state
    if hasattr(st.session_state, 'question_set') and st.session_state.question_set:
        question_set = st.session_state.question_set
        
        # Initialize current question index if not exists
        if 'current_question_idx' not in st.session_state:
            st.session_state.current_question_idx = 0
            st.session_state.score = 0
            st.session_state.answered = False
        
        # Define callback functions for navigation
        def next_question(points=0):
            st.session_state.score += points
            st.session_state.current_question_idx += 1
            st.session_state.answered = False
        
        # Get current question
        current_idx = st.session_state.current_question_idx
        total_questions = len(question_set.questions)
        
        # Debug information (can be removed later)
        with st.expander("Debug Info"):
            st.write(f"Current Question Index: {current_idx}")
            st.write(f"Total Questions: {total_questions}")
            st.write(f"Score: {st.session_state.score}")
            st.write(f"Answered: {st.session_state.answered}")
            if st.button("Reset Session", key="reset_debug"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.experimental_rerun()
        
        if current_idx < total_questions:
            question = question_set.questions[current_idx]
            
            # Progress bar
            st.progress((current_idx) / total_questions)
            st.markdown(f"**Question {current_idx + 1} of {total_questions}**")
            
            # Display question
            st.markdown(f"""
            <div class='question-box'>
                <h3>{question.text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # User answer
            user_answer = st.text_area("Your Answer", height=100, key=f"answer_{current_idx}")
            
            # Check answer button
            if st.button("Check Answer", key=f"check_{current_idx}"):
                st.session_state.answered = True
                
                # Display correct answer
                st.markdown(f"""
                <div class='answer-box'>
                    <h4>Correct Answer:</h4>
                    <p style="font-weight: 500;">{question.answer}</p>
                </div>
                <div class='explanation-box'>
                    <h4>Explanation:</h4>
                    <p style="font-weight: 500;">{question.explanation}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Self-evaluation
                st.markdown("### How did you do?")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("I got it right! ✅", key=f"correct_{current_idx}", on_click=next_question, args=(1,)):
                        pass
                
                with col2:
                    if st.button("I was close 🤔", key=f"close_{current_idx}", on_click=next_question, args=(0.5,)):
                        pass
                
                with col3:
                    if st.button("I was wrong ❌", key=f"wrong_{current_idx}", on_click=next_question, args=(0,)):
                        pass
        
        else:
            # Quiz completed
            st.markdown(f"""
            <div class='success-box'>
                <h2>🎉 Congratulations!</h2>
                <h3>You've completed all questions!</h3>
                <p>Your score: {st.session_state.score} / {total_questions}</p>
                <p>Accuracy: {(st.session_state.score / total_questions) * 100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Define callback functions
            def reset_quiz():
                st.session_state.current_question_idx = 0
                st.session_state.score = 0
                st.session_state.answered = False
            
            def go_to_youtube():
                st.session_state.selected = "YouTube Transcript"
            
            # Reset button
            if st.button("Start Over", key="start_over", on_click=reset_quiz):
                pass
            
            # Process new video button
            if st.button("Process New Video", key="new_video", on_click=go_to_youtube):
                pass
    
    else:
        st.info("No questions available. Please process a YouTube video first.")
        
        # Example videos
        st.markdown("### Try these example videos:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **TED Talk: The Power of Vulnerability**  
            https://www.youtube.com/watch?v=iCvmsMzlF7o
            """)
        
        with col2:
            st.markdown("""
            **TED-Ed: How sugar affects the brain**  
            https://www.youtube.com/watch?v=lEXBxijQREo
            """)
        
        # Button to go to YouTube Transcript section
        if st.button("Go to YouTube Transcript"):
            st.session_state.selected = "YouTube Transcript"
            st.experimental_rerun()

# History section
elif selected == "History":
    st.markdown("<h2 class='sub-header'>History</h2>", unsafe_allow_html=True)
    st.markdown("View your previously processed videos and questions.")
    
    # Import vector store manager
    from backend.vector_store import VectorStoreManager
    
    # Initialize vector store manager
    vector_store = VectorStoreManager()
    
    # Get all transcripts
    try:
        all_transcripts = vector_store.get_all_transcripts()
        
        if all_transcripts:
            st.markdown(f"Found {len(all_transcripts)} processed videos.")
            
            for i, transcript in enumerate(all_transcripts, 1):
                try:
                    # Get a display title for the transcript
                    display_title = transcript.url if transcript.url else f"Transcript {transcript.video_id}"
                    
                    with st.expander(f"Video {i}: {display_title}"):
                        if transcript.url:
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
                                    st.markdown(f"""
                                    <div class='question-box'>
                                        <h4>Question {j}: {question.text}</h4>
                                        <div class='answer-box'>
                                            <p><strong>Answer:</strong> {question.answer}</p>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Button to practice with this question set
                                if st.button(f"Practice with this video #{i}", key=f"practice_{i}"):
                                    # Create a question set and store in session state
                                    from models.schemas import QuestionSet
                                    
                                    # Create metadata with available information
                                    metadata = {'language': transcript.language}
                                    if transcript.url:
                                        metadata['url'] = transcript.url
                                    
                                    question_set = QuestionSet(
                                        id=str(uuid.uuid4()),
                                        transcript_id=transcript.video_id,
                                        questions=questions,
                                        metadata=metadata
                                    )
                                    st.session_state.question_set = question_set
                                    st.session_state.current_question_idx = 0  # Reset question index
                                    st.session_state.score = 0  # Reset score
                                    st.session_state.answered = False  # Reset answered state
                                    st.session_state.selected = "Interactive Learning"
                                    st.experimental_rerun()
                            else:
                                st.markdown("No questions found for this transcript.")
                        except Exception as e:
                            st.error(f"Error getting questions for transcript: {str(e)}")
                except Exception as e:
                    st.error(f"Error displaying transcript {i}: {str(e)}")
                    continue
        else:
            st.info("No processed videos found in history.")
            
    except Exception as e:
        st.error(f"Error getting all transcripts: {str(e)}")
        st.markdown("Make sure you have processed at least one video first.")

# Footer
st.markdown("---")
st.markdown("### Need help?")
st.markdown("""
- Make sure the YouTube video has captions/transcripts available
- For best results, use videos with clear speech and good audio quality
- If you encounter errors, try a different video or language
""") 