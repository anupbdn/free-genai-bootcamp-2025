import sqlite3
from pathlib import Path
from .utils import setup_path

setup_path()
from src.core.config import settings

def run_migrations():
    print("Starting database migrations...")
    conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.executescript("""
        DROP TABLE IF EXISTS word_review_items;
        DROP TABLE IF EXISTS study_sessions;
        DROP TABLE IF EXISTS study_activities;
        DROP TABLE IF EXISTS words_groups;
        DROP TABLE IF EXISTS words;
        DROP TABLE IF EXISTS groups;
    """)
    
    migrations_dir = Path(settings.MIGRATIONS_DIR)
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    for migration_file in migration_files:
        print(f"Running migration: {migration_file.name}")
        with open(migration_file) as f:
            sql = f.read()
            cursor.executescript(sql)
    
    conn.commit()
    conn.close()
    print("Migrations completed successfully")

if __name__ == "__main__":
    run_migrations() 