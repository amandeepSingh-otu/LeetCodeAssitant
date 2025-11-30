from fastapi import APIRouter
from models.requestClasses import edge_or_complexity_request
from services import edgeCaseService

router = APIRouter()

@router.post("/generate_edge_cases")
def generate_edge_cases(req: edge_or_complexity_request):
    hint= edgeCaseService.EdgeCaseService().generate_edge_case_hint(req)
    return {
        "hint":hint
    }
