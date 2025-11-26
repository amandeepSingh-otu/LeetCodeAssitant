import json
from services.llm_client import LLMClient

class HintService:
    def __init__(self):
        self.llm = LLMClient()
        with open("config/prompts.json") as f:
            self.prompts = json.load(f)

    def generate_hint(self, req):
        template = self.prompts["apis"]["hint"]
        code_policy= self.prompts["code_policy"]
        output_format= self.prompts["output_format"]
        persona= self.prompts["persona"]

        # Always include slug + description
        values = {
            "description": req.description,
        }

        parts = [
            template["description"].format(**values),
        ]

        # Only include solution if provide_code is True
        if req.solution:
            values["solution"] = req.solution
            parts.append(template["solution"].format(**values))

        # Only include chat_history if not empty
        if req.chat_history:
            values["chat_history"] = req.chat_history
            parts.append(template["chat_history"].format(**values))

        # Always include the task instruction
        parts.append(template["task"].format(**values))

        if req.provide_code:
            code_policy= code_policy['generate']
        else:
            code_policy= code_policy['dont_generate']

        prompt = persona+ "\n".join(parts) + "\n" + code_policy + "\n" + output_format

        # Call Gemini
        return self.llm.ask(prompt, pathway="RAG")
