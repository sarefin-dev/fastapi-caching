import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging_config import setup_logger
from app.core.settings.config import ConfigDep, get_app_config
from app.routes import basic_computation

logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_settings = await get_app_config()
    await setup_logger(app_settings)
    logger = logging.getLogger(app_settings.logger_name)
    logger.info(f"Starting {app.title}")
    yield
    logger.info(f"Shutting down {app.title}")


app = FastAPI(
    title="With Cachetool",
    lifespan=lifespan,
    version="1.0.0",
    description="We will explore various use cases of cachetool here",
    swagger_ui_parameters={"displayRequestDuration": True},
)

app.include_router(basic_computation.router)


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
async def root(request: Request, settings: ConfigDep):
    """
    Root endpoint - API information and navigation.

    Provides metadata about the API including version, status,
    and links to documentation and available endpoints.
    """

    base_url = str(request.base_url).rstrip("/")
    return {
        "message": f"{app.title}:{settings.app_name}",
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
