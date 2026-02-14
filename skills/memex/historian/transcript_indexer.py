#!/usr/bin/env python3
"""
Transcript Indexer - Index Plaud transcripts using FAISS + sentence-transformers

Self-contained: uses FAISS for vector search, no ChromaDB dependency.
Works with Python 3.14.

Handles the Plaud export format:
  each_transcript_dir/
    transcript.json   - [{speaker, content, start_time, end_time}, ...]
    notes.md          - AI notes in markdown
    metadata.json     - {file_id, filename, duration_ms, start_time, ...}
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Config
CHUNK_SIZE = 500  # characters
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = DATA_DIR / "faiss_index"
PLAUD_EXPORT_DIR = BASE_DIR.parent / "data" / "plaud_transcripts"
LOOM_EXPORT_DIR = BASE_DIR.parent / "data" / "loom_transcripts"

INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Index file paths
FAISS_INDEX_PATH = INDEX_DIR / "transcripts.faiss"
METADATA_PATH = INDEX_DIR / "transcripts_meta.pkl"
INDEXED_FILE = PLAUD_EXPORT_DIR / "indexed_vectordb.json"


class TranscriptIndexer:
    """Index Plaud transcripts using FAISS + local sentence-transformers"""

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # Load or create FAISS index
        if FAISS_INDEX_PATH.exists() and METADATA_PATH.exists():
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
            with open(METADATA_PATH, "rb") as f:
                self.metadata_store = pickle.load(f)
            logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
        else:
            self.index = faiss.IndexFlatIP(EMBEDDING_DIM)  # Inner product (cosine after normalization)
            self.metadata_store = []  # list of {document, metadata} dicts
            logger.info("Created new FAISS index")

    def _save_index(self):
        """Persist FAISS index and metadata to disk"""
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(self.metadata_store, f)

    def _load_indexed(self) -> Dict[str, str]:
        if INDEXED_FILE.exists():
            with open(INDEXED_FILE) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return {item: "" for item in data}
                return data
        return {}

    def _save_indexed(self, indexed: Dict[str, str]):
        with open(INDEXED_FILE, "w") as f:
            json.dump(indexed, f, indent=2)

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate normalized embeddings"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Normalize for cosine similarity via inner product
        faiss.normalize_L2(embeddings)
        return embeddings

    def index_directory(self, directory: Path = None) -> Dict:
        """Index all Plaud transcript directories"""
        if directory is None:
            directory = PLAUD_EXPORT_DIR

        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return {"new": 0, "skipped": 0, "errors": 0, "chunks": 0}

        indexed = self._load_indexed()
        stats = {"new": 0, "skipped": 0, "errors": 0, "chunks": 0}

        transcript_dirs = sorted([
            d for d in directory.iterdir()
            if d.is_dir() and (d / "transcript.json").exists()
        ])

        logger.info(f"Found {len(transcript_dirs)} transcript directories in {directory}")

        for tdir in transcript_dirs:
            dir_name = tdir.name
            meta_path = tdir / "metadata.json"

            if meta_path.exists():
                with open(meta_path) as f:
                    meta = json.load(f)
                file_id = meta.get("file_id", dir_name)
            else:
                file_id = dir_name

            if file_id in indexed:
                stats["skipped"] += 1
                continue

            try:
                chunks = self._index_one(tdir, file_id)
                indexed[file_id] = dir_name
                stats["new"] += 1
                stats["chunks"] += chunks
                if stats["new"] % 50 == 0:
                    logger.info(f"Progress: {stats['new']} indexed, {stats['skipped']} skipped, {stats['chunks']} chunks")
                    self._save_indexed(indexed)
                    self._save_index()
            except Exception as e:
                logger.error(f"Error indexing {dir_name}: {e}")
                stats["errors"] += 1

        self._save_indexed(indexed)
        self._save_index()
        logger.info(f"Indexing complete: {stats}")
        return stats

    def _index_one(self, tdir: Path, file_id: str) -> int:
        """Index a single transcript directory"""
        meta = {}
        meta_path = tdir / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)

        filename = meta.get("filename", tdir.name)
        duration_ms = meta.get("duration_ms", 0)
        start_time = meta.get("start_time", 0)

        if start_time:
            date_str = datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        transcript_path = tdir / "transcript.json"
        with open(transcript_path) as f:
            segments = json.load(f)

        if not segments:
            return 0

        documents = []
        metadatas = []

        current_chunk = []
        current_len = 0
        current_speakers = set()
        chunk_start_time = None

        def flush_chunk(chunk_idx):
            if not current_chunk:
                return
            text = "\n".join(current_chunk)
            documents.append(text)
            metadatas.append({
                "transcript_id": file_id,
                "chunk_index": chunk_idx,
                "date": date_str,
                "title": filename,
                "speakers": ", ".join(sorted(s for s in current_speakers if s)),
                "duration_ms": duration_ms,
                "start_time_ms": chunk_start_time or 0,
                "source_dir": tdir.name,
                "content_type": "transcript",
            })

        chunk_idx = 0
        for seg in segments:
            speaker = seg.get("speaker") or "Unknown"
            content = (seg.get("content") or "").strip()
            seg_start = seg.get("start_time", 0)

            if not content:
                continue

            line = f"{speaker}: {content}"

            if current_len + len(line) > CHUNK_SIZE and current_chunk:
                flush_chunk(chunk_idx)
                chunk_idx += 1
                overlap_line = current_chunk[-1] if current_chunk else ""
                current_chunk = [overlap_line] if overlap_line else []
                current_len = len(overlap_line)
                current_speakers = set()
                chunk_start_time = seg_start

            if chunk_start_time is None:
                chunk_start_time = seg_start

            current_chunk.append(line)
            current_len += len(line) + 1
            current_speakers.add(speaker)

        if current_chunk:
            flush_chunk(chunk_idx)

        # Also index notes
        notes_path = tdir / "notes.md"
        if notes_path.exists():
            notes_text = notes_path.read_text().strip()
            if notes_text:
                for i in range(0, len(notes_text), CHUNK_SIZE):
                    chunk_text = notes_text[i:i + CHUNK_SIZE]
                    chunk_idx += 1
                    documents.append(chunk_text)
                    metadatas.append({
                        "transcript_id": file_id,
                        "chunk_index": chunk_idx,
                        "date": date_str,
                        "title": filename,
                        "speakers": "AI Summary",
                        "duration_ms": duration_ms,
                        "content_type": "summary",
                        "source_dir": tdir.name,
                    })

        if not documents:
            return 0

        # Generate embeddings and add to FAISS
        embeddings = self._embed_batch(documents)
        self.index.add(embeddings)

        # Store metadata (parallel to FAISS index positions)
        for doc, meta in zip(documents, metadatas):
            self.metadata_store.append({"document": doc, "metadata": meta})

        return len(documents)

    def search(self, query: str, n_results: int = 10, where: dict = None) -> dict:
        """Search the transcript index, returns ChromaDB-compatible dict format"""
        if self.index.ntotal == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        query_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_emb)

        n = min(n_results, self.index.ntotal)
        scores, indices = self.index.search(query_emb, n)

        documents = []
        metadatas = []
        distances = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata_store):
                continue
            entry = self.metadata_store[idx]
            meta = entry["metadata"]

            # Apply where filter if provided
            if where:
                match = True
                for k, v in where.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            documents.append(entry["document"])
            metadatas.append(meta)
            # Convert similarity score to distance (1 - similarity) for compatibility
            distances.append(float(1.0 - score))

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
        }

    def reindex_all(self, directory: Path = None):
        """Clear index and reindex everything"""
        logger.warning("Clearing index and reindexing all transcripts...")
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.metadata_store = []
        if INDEXED_FILE.exists():
            INDEXED_FILE.unlink()
        return self.index_directory(directory)

    def index_all_sources(self) -> Dict:
        """Index all transcript sources (Plaud + Loom)"""
        total = {"new": 0, "skipped": 0, "errors": 0, "chunks": 0}
        for directory in [PLAUD_EXPORT_DIR, LOOM_EXPORT_DIR]:
            if directory.exists():
                logger.info(f"Indexing source: {directory}")
                stats = self.index_directory(directory)
                for k in total:
                    total[k] += stats[k]
            else:
                logger.info(f"Skipping (not found): {directory}")
        return total

    def stats(self) -> Dict:
        """Return current index statistics"""
        indexed = self._load_indexed()
        return {
            "total_chunks": self.index.ntotal,
            "indexed_transcripts": len(indexed),
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Plaud Transcript Indexer")
    parser.add_argument("--directory", type=str, help="Directory to index",
                        default=str(PLAUD_EXPORT_DIR))
    parser.add_argument("--reindex", action="store_true", help="Clear and reindex all")
    parser.add_argument("--all-sources", action="store_true", help="Index all sources (Plaud + Loom)")
    parser.add_argument("--stats", action="store_true", help="Show index stats")
    parser.add_argument("--search", type=str, help="Search query")

    args = parser.parse_args()

    indexer = TranscriptIndexer()

    if args.stats:
        s = indexer.stats()
        print(f"\nIndex Stats:")
        print(f"  Total chunks: {s['total_chunks']}")
        print(f"  Indexed transcripts: {s['indexed_transcripts']}")
        return

    if args.search:
        results = indexer.search(args.search)
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )):
            print(f"\n--- Result {i+1} (score: {1-dist:.3f}) ---")
            print(f"  Title: {meta.get('title', '?')}")
            print(f"  Date: {meta.get('date', '?')}")
            print(f"  Speakers: {meta.get('speakers', '?')}")
            print(f"  {doc[:200]}...")
        return

    if args.reindex:
        stats = indexer.reindex_all(Path(args.directory))
    elif args.all_sources:
        stats = indexer.index_all_sources()
    else:
        stats = indexer.index_directory(Path(args.directory))

    print(f"\nIndexing complete:")
    print(f"  New: {stats['new']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Chunks: {stats['chunks']}")


if __name__ == "__main__":
    main()
