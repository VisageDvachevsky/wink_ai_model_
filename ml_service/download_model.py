#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")


def download_model():
    model_id = os.getenv("ML_HUGGINGFACE_MODEL_ID", "")
    token = os.getenv("ML_HUGGINGFACE_TOKEN", "")
    cache_dir = os.getenv("ML_MODELS_CACHE_DIR", "./models_cache")

    if not model_id:
        logger.error("ML_HUGGINGFACE_MODEL_ID not set")
        sys.exit(1)

    logger.info(f"Downloading model {model_id} to {cache_dir}")
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    try:
        model = SentenceTransformer(
            model_id, cache_folder=cache_dir, token=token if token else None
        )
        logger.info(f"Model downloaded successfully: {model_id}")
        logger.info(f"Model dimension: {model.get_sentence_embedding_dimension()}")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()
