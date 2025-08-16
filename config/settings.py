
"""
Configuration settings for Bhagavad Gita AI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
UI_DIR = BASE_DIR / "ui"

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_MODELS = {
    "fast": "llama3-8b-8192",
    "balanced": "llama3-70b-8192", 
    "creative": "mixtral-8x7b-32768"
}

# App Configuration
APP_CONFIG = {
    "name": "🕉️ Bhagavad Gita AI",
    "version": "1.0.0",
    "description": "AI-powered Bhagavad Gita wisdom guide with voice interaction",
    "author": "Vineet Yadav"
}

# Voice Configuration
VOICE_CONFIG = {
    "enabled": os.getenv("VOICE_ENABLED", "true").lower() == "true",
    "languages": {
        "english": "en-US",
        "hindi": "hi-IN",
        "sanskrit": "sa-IN"
    },
    "tts_rate": 150,
    "tts_volume": 0.8
}

# UI Configuration
UI_CONFIG = {
    "theme": "dark",
    "primary_color": "#FF6B35",
    "background_color": "#0E1117", 
    "text_color": "#FAFAFA",
    "animation_speed": "0.3s"
}

# Data Configuration
DATA_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "max_search_results": 5,
    "similarity_threshold": 0.7,
    "cache_embeddings": True
}

# Groq Configuration
GROQ_CONFIG = {
    "default_model": GROQ_MODELS["fast"],
    "max_tokens": 1500,
    "temperature": 0.7,
    "timeout": 30
}

