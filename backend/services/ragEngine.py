import json
import os
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv



'''This class takes in a problem description and finds the nearest neighbor from the existing problems database using embeddings.
If a very similar problem already exists, it returns None to avoid redundancy. Otherwise, it returns details of the closest matching problem.
the embedding contains problems which are super common and LLM understands well how to solve them, so we can provide better hints/guidance based on those solutions.'''



class RAGEngine:
    def __init__(self, vector_store_path="data/embeddings/vectorStore.json", problems_path="data/problemsJson/problemsFinal.json"):
        # 1. Load Config & API
        load_dotenv(dotenv_path=os.path.join("config", ".env"))
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please check config/.env")

        genai.configure(api_key=api_key)
        self.embedding_model = "models/text-embedding-004"

    
        if not os.path.exists(vector_store_path):
            raise FileNotFoundError(f"Vector store not found at {vector_store_path}. Run generate_embeddings.py first.")

        with open(vector_store_path, 'r') as f:
            self.vector_store = json.load(f)

       
        for item in self.vector_store:
            item['embedding'] = np.array(item['embedding'])

        self.existing_descriptions = set()
        if os.path.exists(problems_path):
            with open(problems_path, 'r') as f:
                raw_data = json.load(f)
                for p in raw_data:
                    desc = p.get("description", "")
                    if desc:
                        self.existing_descriptions.add(desc.strip())

    def _get_embedding(self, text: str) -> np.ndarray:
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query", 
            )
            return np.array(result['embedding'])
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None

    def _cosine_similarity(self, vec_a, vec_b):
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def find_nearest_neighbor(self, description: str):
      
       
        if description.strip() in self.existing_descriptions:
            return None

     
        query_vector = self._get_embedding(description)
        if query_vector is None:
            return None

        best_score = -1.0
        best_match = None

    
        for item in self.vector_store:
            score = self._cosine_similarity(query_vector, item['embedding'])
            
            if score > best_score:
                best_score = score
                best_match = item

   
        if best_score > 0.99: 
            return None

      
        return {
            "similar_problem": best_match['slug'],
            "similarity_score": best_score,
            "solution_guidance": best_match['solution']
        }
