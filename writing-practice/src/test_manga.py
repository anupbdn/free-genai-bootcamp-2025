from manga_ocr import MangaOcr
from PIL import Image
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

kakasi = pykakasi.kakasi()
kakasi.setMode("H", "a")  # Convert Hiragana to ascii
kakasi.setMode("K", "a")  # Convert Katakana to ascii
kakasi.setMode("J", "a")  # Convert Japanese to ascii
kakasi.setMode("r", "Hepburn")  # Use Hepburn romanization
converter = kakasi.getConverter()

# Load image
image = Image.open('original-o.png')

# Get cached MangaOCR instance
mocr = get_manga_ocr()

# Perform OCR
text = mocr(image)
# Convert to romaji
romaji_text = converter.do(text)

print("Japanese text:", text)
print("Romaji text:", romaji_text)