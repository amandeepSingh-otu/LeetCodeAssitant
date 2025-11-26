# backend/llm_client.py
import os
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
import google.generativeai as genai
import requests

class LLMClient:
    """
    Centralized client for Gemini requests with telemetry logging and rate-limit handling.
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        load_dotenv(dotenv_path=os.path.join("config", ".env"))

        # Configure logging
        logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/telemetry.log"),   # write logs to a file
        logging.StreamHandler()                 # still print to console
    ]
)
        self.logger = logging.getLogger(__name__)

        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3-pro-preview")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

        # Rate-limit config
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def ask(self, prompt: str, pathway: str = "none") -> str:
        """
        Send a prompt to Gemini with retry/backoff on rate-limit errors.
        Logs telemetry: timestamp, pathway, latency, model, and token usage.
        """
        start_time = time.time()
        attempt = 0

        while attempt < self.max_retries:
            try:
                response = self.model.generate_content(prompt)

                latency = round((time.time() - start_time) * 1000, 2)  # ms
                timestamp = datetime.now(timezone.utc).isoformat()

                # Extract usage metadata if available
                usage = getattr(response, "usage_metadata", None)
                prompt_tokens = usage.prompt_token_count if usage else None
                output_tokens = usage.candidates_token_count if usage else None
                total_tokens = usage.total_token_count if usage else None

                telemetry = {
                    "timestamp": timestamp,
                    "pathway": pathway,
                    "latency_ms": latency,
                    "model": self.model_name,
                    "prompt_tokens": prompt_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                }

                self.logger.info(f"Telemetry: {telemetry}")
                return response.text

            except Exception as e:
                attempt += 1
                latency = round((time.time() - start_time) * 1000, 2)
                timestamp = datetime.now(timezone.utc).isoformat()

                # Log error telemetry
                self.logger.error(
                    f"Telemetry: {{'timestamp': '{timestamp}', 'pathway': '{pathway}', 'latency_ms': {latency}, 'error': '{e}', 'attempt': {attempt}}}"
                )

                # Handle rate-limit (429) with backoff
                if hasattr(e, "response") and getattr(e.response, "status_code", None) == 429:
                    sleep_time = self.backoff_factor ** attempt
                    self.logger.warning(f"Rate limit hit. Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    # Non-rate-limit error → break immediately
                    break

        return "Sorry, I couldn't generate a response at this time."

