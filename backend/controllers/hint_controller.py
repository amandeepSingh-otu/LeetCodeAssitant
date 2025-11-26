from services import hint_service
from fastapi import APIRouter
from models.request_classes import hint_request

router = APIRouter()

@router.post("/get_hint")
def get_hint(req: hint_request):
    ''' Coming from request:
             Slug: Unique identifier for the problem on LeetCode.
            description: The full problem description along with example of problem and contraints 
                        extratced from LeetCode.
            solution: (Optional) the cod euser currently have in the leetcode editor.
            provide_code: to check if user wants code along with hint.
            chat_history: (Optional) previous chat history for context in hints
            '''
    
    hint= hint_service.HintService().generate_hint(req)
    return {
        "hint":hint
    }
