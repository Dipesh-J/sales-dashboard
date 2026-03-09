import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.router import api_router
from .core.config import settings
from .core.cache import init_redis

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    init_redis()
    yield


app = FastAPI(
    title="Sales Dashboard API",
    description="Full-stack sales & store analytics dashboard API. Provides sales metrics, active store analytics, and multi-dimensional filtering with CSV/XLSX data upload.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

logger.info(
    "Sales Dashboard API started (DEBUG=%s, CORS=%s)",
    settings.DEBUG,
    settings.CORS_ORIGINS,
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Sales Dashboard API"}
