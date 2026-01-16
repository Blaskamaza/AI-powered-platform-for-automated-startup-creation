"""
UZ AI Factory Configuration

All agents are now V2 (Skills + Worktrees).
V1 code is archived in legacy/v1 branch.
"""

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
GEMINI_PRO_MODEL = "gemini-2.0-flash"
GEMINI_FLASH_MODEL = "gemini-2.0-flash"

# Worktree Output (V2 is now default)
WORKTREE_DIR = BASE_DIR / "worktrees"

# Legacy Data Dir (for migration purposes)
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"

# Rollout settings (Canary deployment)
V2_ROLLOUT_PERCENTAGE = int(os.getenv("V2_ROLLOUT_PERCENTAGE", "100"))  # 100% = V2 only
V2_MAX_PARALLEL_TASKS = int(os.getenv("V2_MAX_PARALLEL_TASKS", "5"))
