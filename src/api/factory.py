"""Application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src import __version__
from src.api_middleware import RequestIdMiddleware, SimpleRateLimitMiddleware
from src.api.deps import STATIC_DIR, clear_settings_cache, get_settings, log, setup_logging
from src.config import get_settings as _gs


@asynccontextmanager
async def _lifespan(app: FastAPI):
    clear_settings_cache()
    setup_logging(get_settings().log_level)
    log.info("API v%s starting", __version__)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chokepoint Research Agent",
        description=(
            "Professional multi-agent research workstation powered by Chokepoint Theory. "
            "Research/education only — not investment advice."
        ),
        version=__version__,
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _s0 = _gs()
    app.add_middleware(
        SimpleRateLimitMiddleware,
        max_requests=_s0.api_rate_limit,
        window_seconds=_s0.api_rate_window_seconds,
    )
    app.add_middleware(RequestIdMiddleware)
    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    from src.api.routes import core, coverage, knowledge, ops, pro, reports, research

    for mod in (core, research, coverage, reports, pro, knowledge, ops):
        mod.register(app)

    return app
