import streamlit as st
import requests
import json
import re

# Ollama API endpoint for Mistral
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Function to query Mistral via Ollama
def get_vocab_from_ollama(text):
    payload = {
        "model": "mistral:latest",  # Using the installed model version
        "prompt": (
            f"Given this English word or phrase, provide the Japanese translation with its reading in hiragana and romaji. "
            f"Format each item as 'japanese (hiragana) [romaji]: english'. "
            f"If there are multiple common translations, provide the most relevant ones. "
            f"Example: '猫 (ねこ) [neko]: cat'. Text: {text}"
        ),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        raw_output = response.json().get("response", "")
        return parse_mistral_output(raw_output)
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Ollama: {e}")
        return None

# Parse Mistral's text output into structured JSON
def parse_mistral_output(output):
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

# Streamlit app
st.title("Japanese Vocabulary Generator Tool")
st.write("Generate Japanese vocabulary from English words or phrases.")

# Tabs for Generate and Import functionality
tab1, tab2 = st.tabs(["Generate Vocabulary", "Import Vocabulary"])

# Tab 1: Generate Vocabulary
with tab1:
    st.subheader("Generate Vocabulary")
    input_text = st.text_area("Enter English word or phrase", "", key="generate_input")
    
    if st.button("Generate", key="generate_btn"):
        if input_text:
            with st.spinner("Generating Japanese vocabulary with Mistral..."):
                vocab_data = get_vocab_from_ollama(input_text)
                if vocab_data and vocab_data["vocabulary"]:
                    st.session_state["generated_vocab"] = vocab_data  # Store in session state
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

# Tab 2: Import Vocabulary
with tab2:
    st.subheader("Import Vocabulary")
    uploaded_file = st.file_uploader("Upload a JSON vocabulary file", type=["json"], key="import_file")
    
    if uploaded_file:
        try:
            # Read and parse the uploaded JSON file
            vocab_data = json.load(uploaded_file)
            if "vocabulary" in vocab_data and isinstance(vocab_data["vocabulary"], list):
                st.session_state["imported_vocab"] = vocab_data  # Store in session state
                st.success("Vocabulary imported successfully!")
                st.json(vocab_data)
            else:
                st.error("Invalid JSON format. Expected {'vocabulary': [...] }")
        except json.JSONDecodeError:
            st.error("Error decoding JSON file. Please check the file format.")
    
    # Export option for imported vocabulary (if modified or reviewed)
    if "imported_vocab" in st.session_state:
        json_str = json.dumps(st.session_state["imported_vocab"], ensure_ascii=False, indent=2)
        st.download_button(
            label="Export Imported JSON",
            data=json_str,
            file_name="imported_japanese_vocab.json",
            mime="application/json",
            key="export_imported_btn"
        )

# Footer
st.write("---")
st.write("Built with Streamlit and Mistral (Ollama) - For internal use only.")