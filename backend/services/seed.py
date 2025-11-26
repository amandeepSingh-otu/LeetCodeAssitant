import json
import os
import logging
import time
from google.generativeai import embed_content

# Correct input/output paths
INPUT_FILE = "data/problemsJson/cleaned_problems_final.json"
OUTPUT_FILE = "data/embeddings/embeddings_only.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/seed.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def generate_embedding(text: str, retries: int = 3, backoff: float = 2.0) -> list:
    """
    Generate embedding vector for given text using Gemini.
    Retries with exponential backoff if quota/rate-limit errors occur.
    """
    attempt = 0
    while attempt < retries:
        try:
            response = embed_content(model="models/embedding-001", content=text)
            return response.get("embedding", [])
        except Exception as e:
            attempt += 1
            wait = backoff ** attempt
            logger.warning(f"Embedding failed (attempt {attempt}): {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)
    logger.error("Embedding failed after retries. Returning empty embedding.")
    return []


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} not found")

    with open(INPUT_FILE) as f:
        problems = json.load(f)

    embeddings_map = {}
    for problem in problems:
        slug = problem["problem_slug"]
        logger.info(f"Processing {slug}...")

        embedding = generate_embedding(problem.get("description", ""))
        embeddings_map[slug] = embedding

    with open(OUTPUT_FILE, "w") as f:
        json.dump(embeddings_map, f, indent=2)

    logger.info(f"Embeddings saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
