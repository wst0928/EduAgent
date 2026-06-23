"""FastAPI application entry point with static file serving."""
from __future__ import annotations

import os
import mimetypes
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import settings

# Register correct MIME types for static files
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")


# Resolve frontend dist paths
_frontend_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "frontend", "dist",
)
_assets_dir = os.path.join(_frontend_dir, "assets")
_index_path = os.path.join(_frontend_dir, "index.html")

# Read and fix index.html (strip crossorigin since same-origin)
_frontend_html = ""
if os.path.isfile(_index_path):
    with open(_index_path, "r", encoding="utf-8") as f:
        _frontend_html = f.read()
    _frontend_html = _frontend_html.replace(' crossorigin', '')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print(f"  {settings.app_name} v{settings.app_version} starting up...")
    yield
    print("  Shutting down EduAgent...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# Serve root
@app.get("/")
async def serve_frontend():
    if _frontend_html:
        return HTMLResponse(_frontend_html)
    return {"service": settings.app_name, "version": settings.app_version}


# Serve static assets
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

# Serve favicon
_vite_svg = os.path.join(_frontend_dir, "vite.svg")
if os.path.isfile(_vite_svg):
    @app.get("/vite.svg")
    async def serve_favicon():
        return FileResponse(_vite_svg, media_type="image/svg+xml")
