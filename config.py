import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
VERTEX_PROJECT_ID = os.getenv("VERTEX_PROJECT_ID")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")

# Models
GEMINI_PRO_MODEL = "gemini-1.5-pro-002"
GEMINI_FLASH_MODEL = "gemini-1.5-flash-002"

# Vibe-Lite / V2 Flags
ENABLE_V2_AGENTS = True  # Enable Skills + Worktrees
V2_OUTPUT_DIR = BASE_DIR / "worktrees"

# Legacy Data Dir
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
