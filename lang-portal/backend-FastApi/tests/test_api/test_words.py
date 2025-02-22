import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))
from src.main import app

client = TestClient(app)

def test_read_words():
    response = client.get("/api/words")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_word(client):
    word_data = {
        "japanese": "テスト",
        "romaji": "tesuto",
        "english": "test",
        "parts": {
            "hiragana": ["て", "す", "と"]
        }
    }
    response = client.post("/api/words", json=word_data)
    assert response.status_code == 200
    data = response.json()
    assert data["japanese"] == word_data["japanese"]
    assert data["english"] == word_data["english"]

def test_get_words(client):
    response = client.get("/api/words")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_word(client):
    # First create a word
    word_data = {
        "japanese": "こんにちは",
        "romaji": "konnichiwa",
        "english": "hello",
        "parts": {
            "hiragana": ["こ", "ん", "に", "ち", "は"]
        }
    }
    create_response = client.post("/api/words", json=word_data)
    word_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/words/{word_id}")
    assert response.status_code == 200
    assert response.json()["japanese"] == word_data["japanese"] 