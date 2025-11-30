from pydantic import BaseModel
from typing import Optional

class edge_or_complexity_request(BaseModel):
    '''     Slug: Unique identifier for the problem on LeetCode.
            description: The full problem description along with example of problem and contraints 
                        extratced from LeetCode.
            solution: (Optional) the cod euser currently have in the leetcode editor.
            provide_code: to check if user wants code along with hint.
            chat_history: (Optional) previous chat history for context in hints.'''

    slug: str
    description: str
    solution: Optional[str] = None
    
class hint_request(BaseModel):
    '''     Slug: Unique identifier for the problem on LeetCode.
            description: The full problem description along with example of problem and contraints 
                        extratced from LeetCode.
            solution: (Optional) the cod euser currently have in the leetcode editor.
            provide_code: to check if user wants code along with hint.
            chat_history: (Optional) previous chat history for context in hints.'''

    slug: str
    description: str
    solution: Optional[str] = None
    provide_code: Optional[str] = None
    chat_history: Optional[list[dict]] = None