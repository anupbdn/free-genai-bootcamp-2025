import sys
from pathlib import Path

def setup_path():
    """Add src directory to Python path"""
    src_path = Path(__file__).parent.parent
    sys.path.append(str(src_path)) 