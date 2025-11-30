import json
import logging
from services.llmClient import LLMClient
from services.ragEngine import RAGEngine
from services.safety import InputValidator

class HintService:
    def __init__(self):
        self.llm = LLMClient()
        
        try:
            self.rag_engine = RAGEngine()
        except Exception as e:
            logging.warning(f"RAG Engine could not be initialized: {e}. RAG features will be disabled.")
            self.rag_engine = None

        try:
            with open("config/prompts.json") as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            raise RuntimeError("config/prompts.json not found. Please ensure the file exists.")

    def generate_hint(self, req):
        print(req)
        
        # 1. Validation 
        InputValidator.check_safety(req)
        if not req.description:
            raise ValueError("Description is required to generate a hint.")

        # 2. Retrieve RAG Context of similar proble which are popular, LLM are good asolving those
        rag_content = ""
        if self.rag_engine:
            try:
                # Find nearest neighbor
                similar_data = self.rag_engine.find_nearest_neighbor(req.description)
                if similar_data:
                    # Format the output for the prompt
                    # We create a string that fits into the "## Similar Problems" section
                    rag_content = (
                        f"Consider this similar problem: {similar_data['similar_problem']}\n"
                        f"Similarity Score: {similar_data['similarity_score']:.2f}\n"
                        f"Relevant Solution Approach:\n{similar_data['solution_guidance']}"
                    )
            except Exception as e:
                logging.error(f"Error retrieving RAG context: {e}")
                # Fallback to empty context on error

        # 3. Build the Prompt
        api_prompts = self.prompts.get("apis", {})
        template = api_prompts.get("hint", {})
        code_policy_config = self.prompts.get("code_policy", {})
        output_format = self.prompts.get("output_format", "")
        persona = self.prompts.get("persona", "")

        values = {
            "description": req.description,
            "solution": "",
            "chat_history": "", 
            "extra_examples": rag_content  # Injected RAG content here
        }

        parts = []

     
        desc_template = template.get("description", "## Problem Statement\n{description}")
        parts.append(desc_template.format(**values))

    
        if values["extra_examples"]:
            examples_template = template.get("examples", "## Similar Problems (for inspiration)\n{extra_examples}")
            parts.append(examples_template.format(**values))

        # 4. Include solution if provided 
        if req.solution:
            values["solution"] = req.solution
            sol_template = template.get("solution", "## Current Code\n{solution}")
            parts.append(sol_template.format(**values))

    
        if req.chat_history:
            formatted_history = ""
            for msg in req.chat_history:
          
                role = getattr(msg, 'role', msg.get('role', 'user'))
                content = getattr(msg, 'content', msg.get('content', ''))
                
                role_name = "Student" if role == 'user' else "Coach"
                formatted_history += f"{role_name}: {content}\n"
            
            values["chat_history"] = formatted_history

            history_template = template.get("old_hints", "## Previous Hints Given\n{chat_history}")
            parts.append(history_template.format(**values))

  
        task_template = template.get("task", "## Task\nProvide a helpful hint based on the context.")
        parts.append(task_template.format(**values))

        # if they wanna see code in hint or not
        if str(getattr(req, 'provide_code', 'false')).lower() == 'true':
            policy = code_policy_config.get('generate', "You may provide code snippets.")
        else:
            policy = code_policy_config.get('dont_generate', "Do not provide code.")

        full_prompt = (
            f"{persona}\n\n" + 
            "\n\n".join(parts) + 
            f"\n\n{policy}\n\n" + 
            output_format
        )

        return self.llm.ask(full_prompt, pathway="RAG")