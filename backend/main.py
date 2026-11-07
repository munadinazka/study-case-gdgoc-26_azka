
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.movies import router as movies_router
from app.routers.watchlist import router as watchlist_router
from app.routers.watched import router as watched_router

# ==========================================
# 1. APPLICATION CONFIGURATION
# ==========================================

app = FastAPI(
    title="FilmLog API",
    description=(
        "REST API for FilmLog - "
        "Movie Watchlist and Review Platform"
    ),
    version="1.0.0",
)


# ==========================================
# 2. CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. REGISTER ROUTERS
# ==========================================

app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(movies_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")
app.include_router(watched_router, prefix="/api")


# ==========================================
# 4. BASIC ENDPOINTS
# ==========================================

@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to FilmLog API!",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "service": "FilmLog API",
    }
