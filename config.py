"""Configuration module for AI Xiaosuo."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "ai_xiaosuo.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# MiniMax API Configuration
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
MINIMAX_MODEL = "abab6.5s-chat"  # MiniMax M2.5

# API Configuration
API_TIMEOUT = 120  # seconds
API_MAX_RETRIES = 3
API_RETRY_DELAY = 2  # seconds

# Token limits
MAX_INPUT_TOKENS = 8000  # Max input context
TARGET_CHAPTER_LENGTH = 3000  # Target words per chapter
MIN_CHAPTER_LENGTH = 1800  # Minimum words per chapter

# Context layers (approximate word limits)
CONTEXT_LAYER_1_PERMANENT = 1500  # World settings
CONTEXT_LAYER_2_OUTLINE = 600  # Volume goals + chapter summaries
CONTEXT_LAYER_3_CHARACTERS = 800  # Character status
CONTEXT_LAYER_4_EVENTS = 400  # Key events
CONTEXT_LAYER_5_RECENT = 5000  # Recent 3 chapters

# Cost tracking (USD per 1M tokens)
TOKEN_COST_INPUT = 0.5  # $0.5 per 1M input tokens
TOKEN_COST_OUTPUT = 1.0  # $1.0 per 1M output tokens
DAILY_TOKEN_LIMIT = 5000000  # 5M tokens daily limit

# Quality thresholds
MIN_QUALITY_SCORE = 0.6
MAX_REPETITION_RATIO = 0.15  # Max 15% repeated sentences

# Prohibited content
PROHIBITED_CATEGORIES = ["politics", "porn", "violence", "illegal"]

# Export formats
EXPORT_FORMATS = ["txt", "docx"]

# UI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
