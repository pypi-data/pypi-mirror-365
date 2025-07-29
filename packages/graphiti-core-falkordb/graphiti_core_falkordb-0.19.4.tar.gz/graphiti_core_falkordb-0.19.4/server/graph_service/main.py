from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from graph_service.config import get_settings
from graph_service.routers import ingest, retrieve, entity_types
from graph_service.zep_graphiti import initialize_graphiti, get_graphiti_instance
from graph_service.entity_type_manager import entity_type_manager
from graph_service.security import SecurityHeaders, get_security_config


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await initialize_graphiti(settings)

    # Initialize entity type manager with database driver and LLM client
    graphiti_instance = get_graphiti_instance()
    if graphiti_instance:
        entity_type_manager.set_driver(graphiti_instance.driver)
        entity_type_manager.set_llm_client(graphiti_instance.llm_client)

    yield
    # Shutdown
    # No need to close Graphiti here, as it's handled per-request


app = FastAPI(
    title="Graphiti Knowledge Graph API",
    description="Secure API for managing knowledge graphs with data isolation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    return SecurityHeaders.add_security_headers(response)

app.include_router(retrieve.router)
app.include_router(ingest.router)
app.include_router(entity_types.router)

# Import and include entities router
from graph_service.routers import entities
app.include_router(entities.router)


@app.get('/healthcheck')
async def healthcheck():
    return JSONResponse(content={'status': 'healthy'}, status_code=200)


@app.get('/security-config')
async def security_config():
    """Get current security configuration (for debugging/monitoring)."""
    config = get_security_config()
    return {
        "security_enabled": config.security_enabled,
        "require_group_id": config.require_group_id,
        "allowed_groups_count": len(config.allowed_groups),
        "rate_limit_requests": config.rate_limit_requests,
        "rate_limit_window": config.rate_limit_window
    }
