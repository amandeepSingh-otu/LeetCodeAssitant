from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import hint_controller, complexity_controller, edge_cases_controller

app = FastAPI()

# Enable CORS for local testing (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hint_controller.router, prefix="/hint")
app.include_router(complexity_controller.router, prefix="/complexity")
app.include_router(edge_cases_controller.router, prefix="/edge_cases")
