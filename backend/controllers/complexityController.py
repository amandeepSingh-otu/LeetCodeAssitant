from services import complexityService
from fastapi import APIRouter
from models.requestClasses import edge_or_complexity_request

router = APIRouter()

@router.post("/task_complexity")
def task_complexity(req: edge_or_complexity_request):
    hint= complexityService.ComplexityService().generate_complexity_hint(req) 
    return {
        "hint":hint
    }
