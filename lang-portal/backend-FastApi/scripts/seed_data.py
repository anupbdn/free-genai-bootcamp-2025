import json
from pathlib import Path
from .utils import setup_path

setup_path()
from src.core.database import SessionLocal
from src.models.word import Word
from src.models.group import Group

def seed_data():
    db = SessionLocal()
    try:
        # Seed basic groups
        groups = {
            "basic_greetings": Group(name="Basic Greetings"),
            "numbers": Group(name="Numbers"),
            "colors": Group(name="Colors"),
            "family": Group(name="Family Members"),
            "basic_verbs": Group(name="Basic Verbs")
        }
        
        for group in groups.values():
            db.add(group)
        db.commit()

        # Seed words from JSON files
        seeds_dir = Path(__file__).parent.parent / "seeds"
        for seed_file in seeds_dir.glob("*.json"):
            group_name = seed_file.stem
            if group_name in groups:
                with open(seed_file) as f:
                    words_data = json.load(f)
                    for word_data in words_data:
                        word = Word(**word_data)
                        word.groups.append(groups[group_name])
                        db.add(word)
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data() 