from fastapi import APIRouter, HTTPException
from src.api.schemas import GeneratePayload
from src.generation.orchestrator import run_rag_pipeline
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1")

@router.post("/content/generate")
async def generate_content(payload: GeneratePayload):
    try:
        result = run_rag_pipeline(payload.dict())
        return {"ok": True, "result": result}
    except Exception as e:
        logger.exception("Failed to generate content")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "ok"}

