from fastapi import APIRouter
from models.request_classes import edge_or_complexity_request
from services import edge_case_service

router = APIRouter()

@router.post("/generate_edge_cases")
def generate_edge_cases(req: edge_or_complexity_request):
    hint= edge_case_service.EdgeCaseService().generate_edge_case_hint(req)
    return {
        "hint":hint
    }
