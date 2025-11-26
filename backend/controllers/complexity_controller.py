from services import complexity_service
from fastapi import APIRouter
from models.request_classes import edge_or_complexity_request

router = APIRouter()

@router.post("/task_complexity")
def task_complexity(req: edge_or_complexity_request):
    hint= complexity_service.ComplexityService().generate_complexity_hint(req) 
    return {
        "hint":hint
    }
