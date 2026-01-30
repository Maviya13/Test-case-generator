from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add the project root directory to sys.path to import ai_tester
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
print(f"DEBUG: sys.path: {sys.path}")
from ai_tester import run_ai_tests

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Assuming React runs on port 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestRunRequest(BaseModel):
    module_name: str
    skip_llm: bool = False
    max_cases: int = 3

@app.get("/")
async def read_root():
    return {"message": "FastAPI backend is running!"}

@app.post("/run-tests")
async def run_tests_endpoint(request: TestRunRequest):
    module_path = f"{request.module_name}.py"
    try:
        results = run_ai_tests(
            module_path=module_path,
            skip_llm=request.skip_llm,
            max_cases=request.max_cases
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))