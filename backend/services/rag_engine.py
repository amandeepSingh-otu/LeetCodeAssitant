import json
import numpy as np
from typing import Dict, Any

class PromptManager:
    def __init__(self, prompts_path="config/prompts.json"):
        with open(prompts_path) as f:
            self.prompts = json.load(f)

    def build(self, api_type: str, allow_code: bool = False, **kwargs) -> str:
        persona = self.prompts["persona"]
        parts = [persona]

        # Concatenate only provided fields
        for template in self.prompts["apis"][api_type]:
            # Fill placeholders if data exists
            filled = template.format(**{k: kwargs.get(k, "") for k in kwargs})
            if any(val for val in kwargs.values()):
                parts.append(filled)

        # Add code policy
        code_policy = self.prompts["code_policy"]["generate"] if allow_code else self.prompts["code_policy"]["dont_generate"]
        parts.append(code_policy)

        return "\n".join(parts)


class RAGEngine:
    def __init__(self, problems_path="data/problems.json"):
        with open(problems_path) as f:
            self.problems = {p["slug"]: p for p in json.load(f)}

    def get_context(self, slug: str) -> Dict[str, Any]:
        problem = self.problems.get(slug)
        if not problem:
            return {"description": "", "embedding": "", "extra_examples": "", "previous_hints": ""}

        # Use summary if embedding exists, else fallback to description + examples
        if problem["embedding"]:
            context = {
                "description": problem["summary"] or problem["description"],
                "embedding": problem["summary"],  # inject compact text, not raw vector
                "extra_examples": "",
                "previous_hints": " ".join(problem["old_hints"])
            }
        else:
            context = {
                "description": problem["description"],
                "embedding": "",
                "extra_examples": ", ".join(problem["extra_examples"]),
                "previous_hints": " ".join(problem["old_hints"])
            }
        return context
