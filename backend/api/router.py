from fastapi import APIRouter
from api.endpoints import projects, sources, transform, outputs, demo, provenance

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(transform.router, prefix="/transform", tags=["transform"])
api_router.include_router(outputs.router, prefix="/outputs", tags=["outputs"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(provenance.router, prefix="/provenance", tags=["provenance"])
