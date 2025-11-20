"""FastAPI server for Longevity RAG system.

Provides REST API endpoints:
- POST /api/v1/query - Query the RAG system
- POST /api/v1/admin/build-index - Trigger ingestion and index building
- GET /health - Health check
- GET / - API documentation

Usage:
    uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import subprocess
import sys
from pathlib import Path

from src.rag.core import LongevityRAG
from src.nlp.embeddings import Embeddings
from src.rag.generator import LLMGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Longevity RAG API",
    description="Retrieval-Augmented Generation system for longevity and aging research",
    version="0.2.0",
    docs_url="/",
    redoc_url="/redoc",
)

# Global RAG instance (lazy loaded)
_rag_instance: Optional[LongevityRAG] = None


def get_rag() -> LongevityRAG:
    """Get or create RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        try:
            # Check if real embeddings and LLM should be used
            import os
            use_real_embeddings = os.environ.get("USE_REAL_EMBEDDINGS", "false").lower() == "true"
            use_openai = os.environ.get("USE_OPENAI", "false").lower() == "true"

            embedder = Embeddings(use_mock=not use_real_embeddings) if use_real_embeddings else None
            generator = LLMGenerator(provider="openai" if use_openai else "mock")

            _rag_instance = LongevityRAG(
                embedder=embedder,
                generator=generator
            )
            logger.info(f"RAG initialized: embeddings={'real' if use_real_embeddings else 'mock'}, "
                       f"generator={generator.provider}")
        except FileNotFoundError as e:
            logger.error(f"RAG initialization failed: {e}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": {
                        "code": "INDEX_NOT_BUILT",
                        "message": str(e)
                    }
                }
            )
    return _rag_instance


# Request/Response models
class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about longevity research")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results to retrieve")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show me evidence for senolytic compounds in mouse models",
                "max_results": 10
            }
        }


class QueryResponse(BaseModel):
    text: str = Field(..., description="Generated answer text")
    citations: List[str] = Field(..., description="List of PMIDs cited")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    papers_found: int = Field(..., description="Number of papers found")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Based on the evidence...",
                "citations": ["PMID:33495399", "PMID:29989283"],
                "confidence": 0.92,
                "papers_found": 47
            }
        }


class ErrorResponse(BaseModel):
    error: dict

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "INDEX_NOT_BUILT",
                    "message": "No vector index found. Please run POST /api/v1/admin/build-index or execute scripts/ingest_sample.py."
                }
            }
        }


class BuildIndexRequest(BaseModel):
    force: bool = Field(False, description="Force rebuild even if index exists")


class BuildIndexResponse(BaseModel):
    status: str
    message: str


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        rag = get_rag()
        return {"status": "healthy", "embeddings": str(rag.embedder), "generator": str(rag.generator)}
    except HTTPException:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "Index not built"}
        )


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system with a natural language question.
    
    Returns synthesized answer with citations to relevant PubMed papers.
    """
    try:
        rag = get_rag()
        result = rag.query(request.question, k=request.max_results)
        
        return QueryResponse(
            text=result["text"],
            citations=result["citations"],
            confidence=result["confidence"],
            papers_found=len(result["citations"])
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "INDEX_NOT_BUILT",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An error occurred processing your query: {str(e)}"
                }
            }
        )


def run_ingestion_script() -> dict:
    """Run the ingestion script in a subprocess."""
    try:
        script_path = Path(__file__).parent.parent.parent / "scripts" / "ingest_sample.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Ingestion completed: {result.stdout}")
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        logger.error(f"Ingestion failed: {e.stderr}")
        return {"status": "error", "output": e.stderr}


@app.post("/api/v1/admin/build-index", response_model=BuildIndexResponse)
async def build_index(request: BuildIndexRequest, background_tasks: BackgroundTasks):
    """Admin endpoint to trigger index building.
    
    Runs the ingestion script to process papers and build the FAISS index.
    This is a long-running operation that runs in the background.
    """
    # Check if index already exists
    index_path = Path("data/embeddings/faiss_index.npz")
    if index_path.exists() and not request.force:
        return BuildIndexResponse(
            status="skipped",
            message="Index already exists. Use force=true to rebuild."
        )
    
    # Run ingestion in background
    def build_task():
        global _rag_instance
        _rag_instance = None  # Reset RAG instance
        result = run_ingestion_script()
        if result["status"] == "success":
            logger.info("Index built successfully, RAG instance will be reinitialized on next query")
        else:
            logger.error(f"Index build failed: {result['output']}")
    
    background_tasks.add_task(build_task)
    
    return BuildIndexResponse(
        status="building",
        message="Index build started in background. Check logs for progress."
    )


@app.get("/api/v1/status")
async def get_status():
    """Get system status including index information."""
    index_path = Path("data/embeddings/faiss_index.npz")
    metadata_path = Path("data/processed/metadata.jsonl")
    
    index_exists = index_path.exists()
    metadata_exists = metadata_path.exists()
    
    status = {
        "index_built": index_exists,
        "index_path": str(index_path),
        "metadata_exists": metadata_exists,
        "metadata_path": str(metadata_path),
    }
    
    if metadata_exists:
        try:
            with open(metadata_path, "r") as f:
                chunk_count = sum(1 for _ in f)
            status["chunks_indexed"] = chunk_count
        except Exception:
            status["chunks_indexed"] = "unknown"
    
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
