import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import io
import random
from manga_ocr import MangaOcr
import pykakasi


# Global variable to store the MangaOCR instance
_mocr_instance = None

def get_manga_ocr():
    """Initialize or return the cached MangaOCR instance."""
    global _mocr_instance
    if _mocr_instance is None:
        print("Loading MangaOCR model...")  # Debug message
        _mocr_instance = MangaOcr()
    return _mocr_instance
# Initialize OCR and romaji converter
mocr = get_manga_ocr()
kakasi = pykakasi.kakasi()
kakasi.setMode("H", "a")  # Convert Hiragana to ascii
kakasi.setMode("K", "a")  # Convert Katakana to ascii
kakasi.setMode("J", "a")  # Convert Japanese to ascii
kakasi.setMode("r", "Hepburn")  # Use Hepburn romanization
converter = kakasi.getConverter()

# Set page config
st.set_page_config(
    page_title="Japanese Writing Practice",
    page_icon="✍️",
    layout="wide"
)

# Initialize session state
if 'current_character' not in st.session_state:
    st.session_state.current_character = {'char': 'あ', 'romaji': 'a'}
if 'practice_mode' not in st.session_state:
    st.session_state.practice_mode = 'hiragana'
if 'stroke_width' not in st.session_state:
    st.session_state.stroke_width = 3
if 'test_character' not in st.session_state:
    st.session_state.test_character = None
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0

# Basic character sets with romaji
HIRAGANA = [
    {'char': 'あ', 'romaji': 'a'}, {'char': 'い', 'romaji': 'i'},
    {'char': 'う', 'romaji': 'u'}, {'char': 'え', 'romaji': 'e'},
    {'char': 'お', 'romaji': 'o'}, {'char': 'か', 'romaji': 'ka'},
    {'char': 'き', 'romaji': 'ki'}, {'char': 'く', 'romaji': 'ku'},
    {'char': 'け', 'romaji': 'ke'}, {'char': 'こ', 'romaji': 'ko'},
    {'char': 'さ', 'romaji': 'sa'}, {'char': 'し', 'romaji': 'shi'},
    {'char': 'す', 'romaji': 'su'}, {'char': 'せ', 'romaji': 'se'},
    {'char': 'そ', 'romaji': 'so'}
]

KATAKANA = [
    {'char': 'ア', 'romaji': 'a'}, {'char': 'イ', 'romaji': 'i'},
    {'char': 'ウ', 'romaji': 'u'}, {'char': 'エ', 'romaji': 'e'},
    {'char': 'オ', 'romaji': 'o'}, {'char': 'カ', 'romaji': 'ka'},
    {'char': 'キ', 'romaji': 'ki'}, {'char': 'ク', 'romaji': 'ku'},
    {'char': 'ケ', 'romaji': 'ke'}, {'char': 'コ', 'romaji': 'ko'},
    {'char': 'サ', 'romaji': 'sa'}, {'char': 'シ', 'romaji': 'shi'},
    {'char': 'ス', 'romaji': 'su'}, {'char': 'セ', 'romaji': 'se'},
    {'char': 'ソ', 'romaji': 'so'}
]

BASIC_KANJI = [
    {'char': '一', 'romaji': 'ichi (one)'}, {'char': '二', 'romaji': 'ni (two)'},
    {'char': '三', 'romaji': 'san (three)'}, {'char': '四', 'romaji': 'shi/yon (four)'},
    {'char': '五', 'romaji': 'go (five)'}, {'char': '六', 'romaji': 'roku (six)'},
    {'char': '七', 'romaji': 'shichi/nana (seven)'}, {'char': '八', 'romaji': 'hachi (eight)'},
    {'char': '九', 'romaji': 'kyuu/ku (nine)'}, {'char': '十', 'romaji': 'juu (ten)'},
    {'char': '日', 'romaji': 'hi/nichi (day/sun)'}, {'char': '月', 'romaji': 'tsuki/getsu (moon/month)'},
    {'char': '火', 'romaji': 'hi/ka (fire)'}, {'char': '水', 'romaji': 'mizu/sui (water)'},
    {'char': '木', 'romaji': 'ki/moku (tree/wood)'}
]

def get_random_character(mode='hiragana'):
    """Get a random character based on the selected mode."""
    character_set = {
        'hiragana': HIRAGANA,
        'katakana': KATAKANA,
        'basic_kanji': BASIC_KANJI
    }[mode]
    return random.choice(character_set)

def main():
    st.title("Japanese Writing Practice ✍️")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Practice mode selection
        practice_mode = st.radio(
            "Select Practice Mode",
            ['hiragana', 'katakana', 'basic_kanji'],
            key='practice_mode'
        )
        
        # Character selection based on mode
        character_set = {
            'hiragana': HIRAGANA,
            'katakana': KATAKANA,
            'basic_kanji': BASIC_KANJI
        }[practice_mode]
        
        # Format display options for selectbox
        char_options = [f"{item['char']} ({item['romaji']})" for item in character_set]
        selected_index = st.selectbox(
            "Select Character to Practice",
            range(len(char_options)),
            format_func=lambda x: char_options[x],
            key='char_index'
        )
        st.session_state.current_character = character_set[selected_index]
        
        # Drawing settings
        st.session_state.stroke_width = st.slider(
            "Stroke Width",
            min_value=1,
            max_value=10,
            value=st.session_state.stroke_width
        )
        
        stroke_color = st.color_picker("Stroke Color", "#000000")
        
        # Add file uploader
        st.markdown("### Upload Image")
        uploaded_file = st.file_uploader(
            "Upload your handwritten character",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image of your handwritten Japanese character"
        )

        # Knowledge Test drawing area in sidebar
        st.write("Knowledge Test Area")
        test_canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=st.session_state.stroke_width,
            stroke_color=stroke_color,
            background_color="#eee",
            height=400,
            width=400,
            drawing_mode="freedraw",
            key="outside_canvas",
        )

        # Add clear button for the knowledge test canvas
        if st.button("Clear Knowledge Test Canvas"):
            st.session_state.pop('outside_canvas', None)
            st.rerun()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["Practice", "Upload", "Knowledge Test"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Practice Area")
            practice_canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=st.session_state.stroke_width,
                stroke_color=stroke_color,
                background_color="#eee",
                height=400,
                width=400,
                drawing_mode="freedraw",
                key="practice_canvas",
            )
        
        with col2:
            st.subheader("Character to Practice")
            st.markdown(
                f"""
                <div style='font-size: 150px; text-align: center;'>
                    {st.session_state.current_character['char']}
                </div>
                <div style='font-size: 30px; text-align: center; color: #666;'>
                    {st.session_state.current_character['romaji']}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Reference information
            st.markdown("### Reference Information")
            if st.session_state.practice_mode == 'hiragana':
                st.write("Hiragana is the basic Japanese syllabary")
            elif st.session_state.practice_mode == 'katakana':
                st.write("Katakana is used primarily for foreign words")
            else:
                st.write("Basic Kanji are the fundamental Chinese characters used in Japanese")
                st.write("Note: Many kanji have multiple readings depending on context")
    
    with tab2:
        st.subheader("Upload Image")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            max_size = (400, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            st.image(image, caption="Uploaded Image")
        else:
            st.info("Upload an image to see it here")
    
    with tab3:
        st.subheader("Test Your Knowledge!")
        
        # Initialize or get new test character first
        if st.button("Get New Character") or st.session_state.test_character is None:
            st.session_state.test_character = get_random_character(st.session_state.practice_mode)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("Please use the drawing area in the sidebar for the knowledge test.")
        
        with col2:
            # Display the romaji to write
            st.markdown(
                f"""
                <div style='font-size: 40px; text-align: center; margin: 20px 0;'>
                    Write the character for:
                    <br>
                    <span style='color: #1f77b4; font-weight: bold;'>
                        {st.session_state.test_character['romaji']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add buttons for checking and revealing
            if st.button("Check Answer"):
                st.session_state.total_questions += 1
                
                if test_canvas_result.image_data is not None:
                    try:
                        # Convert canvas data to PIL Image
                        img_array = test_canvas_result.image_data
                        # Convert RGBA to RGB (white background)
                        white_bg = np.ones((img_array.shape[0], img_array.shape[1], 3), dtype=np.uint8) * 255
                        mask = img_array[:, :, 3] > 0  # Get alpha channel mask
                        white_bg[mask] = img_array[mask][:, :3]  # Copy RGB data where alpha > 0
                        drawn_image = Image.fromarray(white_bg)
                        
                        # Perform OCR
                        detected_text = mocr(drawn_image)
                        # Convert to romaji for additional verification
                        detected_romaji = converter.do(detected_text)
                        
                        # Compare with expected character
                        expected_char = st.session_state.test_character['char']
                        expected_romaji = st.session_state.test_character['romaji'].split()[0]  # Get first word for kanji
                        
                        if detected_text == expected_char:
                            st.session_state.correct_answers += 1
                            st.success(f"✨ Correct! The detected character '{detected_text}' matches!")
                        else:
                            st.error(f"Not quite. You wrote: '{detected_text}', Expected: '{expected_char}'")
                        
                        # Show additional information
                        with st.expander("See OCR Details"):
                            st.write("Detected character:", detected_text)
                            st.write("Detected romaji:", detected_romaji)
                            st.write("Expected character:", expected_char)
                            st.write("Expected romaji:", expected_romaji)
                            
                    except Exception as e:
                        st.error("Could not recognize the character. Please try writing more clearly.")
                        st.info("Tip: Make sure the character is written clearly and centered in the drawing area.")
                else:
                    st.warning("Please draw a character before checking.")
            
            if st.button("Show Answer"):
                st.markdown(
                    f"""
                    <div style='font-size: 80px; text-align: center;'>
                        {st.session_state.test_character['char']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Progress section
            st.markdown("### Your Progress")
            if st.session_state.total_questions > 0:
                accuracy = (st.session_state.correct_answers / st.session_state.total_questions) * 100
                st.metric("Accuracy", f"{accuracy:.1f}%")
            st.metric("Correct Answers", st.session_state.correct_answers)
            st.metric("Total Questions", st.session_state.total_questions)


if __name__ == "__main__":
    main() 