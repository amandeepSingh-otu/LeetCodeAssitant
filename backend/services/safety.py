import re

class InputValidator:
    
    # Heuristic patterns for common Prompt Injection techniques
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"ignore\s+system\s+instructions",
        r"you\s+are\s+now\s+(?!a\s+supportive\s+coding\s+coach)", # Negative lookahead allows reinforcing the valid persona
        r"act\s+as\s+an?\s+unrestricted",
        r"override\s+system",
        r"developer\s+mode",
        r"system\s+prompt",
        r"output\s+initial\s+instructions"
        r"hacked"
    ]

    @classmethod
    def check_safety(cls, req) -> bool:
        """
        Scans any request object for prompt injection patterns.
        Checks common text fields and chat history if present.
        """
        # 1. Check common direct text fields
        # Add any other field names you use across your different request types here
        fields_to_check = [
            'slug',
            'description', 
            'solution',  
            'provide_code', 
        ]
        
        for field in fields_to_check:
            # getattr is safe; it returns None if the object doesn't have the field
            value = getattr(req, field, None)
            if value:
                cls._scan_text(str(value))

        # 2. Check Chat History (if it exists on the object)
        chat_history = getattr(req, 'chat_history', []) or []
        for msg in chat_history:
            # Handle if msg is a dict or an object
            content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')
            cls._scan_text(str(content))

        return True

    @classmethod
    def _scan_text(cls, text: str):
        normalized_text = text.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, normalized_text):
                raise ValueError("Security Alert: Potential prompt injection detected. security Alert")