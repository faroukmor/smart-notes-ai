"""Central configuration for Smart Notes AI.

Single source of truth for: database path, Ollama connection,
model names and RAG retrieval settings.
"""
import os

# --- Paths ---------------------------------------------------------------
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(_CORE_DIR, "database")
DB_NAME = "notes_manager.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)
ASSETS_DIR = os.path.join(
    os.path.dirname(_CORE_DIR), "assets"
)

# --- Ollama --------------------------------------------------------------
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen2.5:1.5b"

# --- RAG retrieval -------------------------------------------------------
SIMILARITY_THRESHOLD = 0.60
TOP_K = 3

# --- LLM generation ------------------------------------------------------
TEMPERATURE = 0
NUM_PREDICT = 256
REPEAT_PENALTY = 1.3
