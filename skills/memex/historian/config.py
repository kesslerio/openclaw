"""
Memex HISTORIAN - Configuration
Centralized settings for the memory system
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
AUDIO_DIR = DATA_DIR / "audio"

# Ensure directories exist
for dir_path in [DATA_DIR, CHROMA_DIR, TRANSCRIPTS_DIR, AUDIO_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Embedding Model (Local sentence-transformers - FREE, no API needed)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Local model, no API cost
EMBEDDING_DIMENSIONS = 384  # all-MiniLM-L6-v2 outputs 384 dimensions

# Text Chunking
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 50  # characters

# Recency Ranker Settings
SIMILARITY_WEIGHT = 0.7  # 70% weight on semantic similarity
RECENCY_WEIGHT = 0.3     # 30% weight on recency
DECAY_RATE = 0.05        # 5% decay per day

# ChromaDB
COLLECTION_NAME = "plaud_transcripts"

# API Settings
API_HOST = os.getenv("MEMEX_API_HOST", "0.0.0.0")  # Bind all interfaces for Tailscale access
API_PORT = 8765
API_RELOAD = True  # Dev mode

# Search Defaults
DEFAULT_RESULTS = 10
MAX_RESULTS = 50

# Metadata Fields
METADATA_FIELDS = [
    "date",
    "title", 
    "speaker",
    "duration",
    "source_file",
    "chunk_index",
]
