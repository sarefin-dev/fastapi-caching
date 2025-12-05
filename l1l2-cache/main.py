from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="L1 & L2 cache example", version="1.0.0")


@app.get("/", tags=["Root"])
async def root(request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "message": f"{app.title}",
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
