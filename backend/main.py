from controllers import complexityController, edgeCasesController
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import hintController

app = FastAPI()

# Enable CORS for local testing (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hintController.router, prefix="/hint")
app.include_router(complexityController.router, prefix="/hint")
app.include_router(edgeCasesController.router, prefix="/hint")
