import json
from services.llmClient import LLMClient
from services.safety import InputValidator

class ComplexityService:
    def __init__(self):
        self.llm = LLMClient()
        with open("config/prompts.json") as f:
            self.prompts = json.load(f)
        self.persona = self.prompts["persona"]
        self.code_policy = self.prompts["code_policy"]
        self.output_format = self.prompts["output_format"]

    def generate_complexity_hint(self, req):

        #do validation for prompt inputs here first
        InputValidator.check_safety(req)

        #build the promt now
        template = self.prompts["apis"]["complexity"]

        values = {
            "description": req.description,
        }

        parts = [
            template["description"].format(**values),
        ]

        if req.solution:
            values["solution"] = req.solution
            parts.append(template["solution"].format(**values))

        parts.append(template["task"].format(**values))

        # Respect code policy
        if getattr(req, "provide_code", False):
            code_policy = self.code_policy["generate"]
        else:
            code_policy = self.code_policy["dont_generate"]

        prompt = self.persona + "\n".join(parts) + "\n" + code_policy + "\n" + self.output_format
         

         #send request to gemini llm
        return self.llm.ask(prompt, pathway="RAG")
