from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{app.title} v{app.version} starting up")
    yield
    logger.info(f"{app.title} v{app.version} is shutting down")


app = FastAPI(
    title="FastAPI Caching Examples",
    description="Exploring cache-related operations in FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.

    :param request: Request object for which this exception happend.
    :type request: Request
    :param exc: The exception that occured.
    :type exc: Exception
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/", tags=["Root"])
async def root(request: Request):
    """
    Root endpoint - API information and navigation.

    Provides metadata about the API including version, status,
    and links to documentation and available endpoints.
    """
    base_url = str(request.base_url).rstrip("/")
    return {
        "message": app.title,
        "version": app.version,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "links": {
            "documentation": {
                "swagger_ui": f"{base_url}/docs",
                "redoc": f"{base_url}/redoc",
                "openapi_spec": f"{base_url}/openapi.json",
            }
        },
    }
