import json
import os
import google.generativeai as genai
from dotenv import load_dotenv



'''This script reads problem descriptions and solutions from a JSON file, generates embedding vectors using the Gemini API,
and saves the embeddings along with problem slugs and solutions into a new JSON file for later use in retrieval tasks. I am not running it
eaach time during start up to save time. Idealy this should run at start of application but for now I will run it manually when needed.'''





INPUT_FILE = "data/problemsJson/problemsFinal.json"
OUTPUT_FILE = "data/embeddings/vectorStore.json"

load_dotenv(dotenv_path=os.path.join("config", ".env"))
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check config/.env")

genai.configure(api_key=api_key)
EMBEDDING_MODEL = "models/text-embedding-004"

def get_embedding(text: str) -> list:
    """
    Generates an embedding vector using the Gemini API.
    """
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
            title="Problem Description"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def process_problems():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find input file at {INPUT_FILE}")
        return

    print(f"Reading from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        raw_problems = json.load(f)

    raw_problems = raw_problems[:200]

    vector_store = []
    total_problems = len(raw_problems)

    for i, problem in enumerate(raw_problems):
        slug = problem.get("problem_slug")
        description = problem.get("description", "")
        solution = problem.get("solution", "")


        if not slug or not description:
            continue

        print(f"Processing [{i+1}/{total_problems}]: {slug}")


        vector = get_embedding(description)

        if not vector:
            print(f"Skipping {slug} due to API error/empty embedding.")
            continue

        record = {
            "slug": slug,
            "solution": solution,
            "embedding": vector
        }
        vector_store.append(record)


    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(vector_store, f)

    print(f"Success! Processed {len(vector_store)} problems.")
    print(f"Embeddings and solutions saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_problems()