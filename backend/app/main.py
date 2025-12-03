from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints import auth, providers, domains, system, metrics
from app.services.scheduler import get_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()
    scheduler.load_all_schedules()
    yield
    # Shutdown
    if scheduler.scheduler.running:
        scheduler.shutdown()

app = FastAPI(title="ip-hop API", version="1.0.0", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API V1 Router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])
app.include_router(domains.router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ip-hop API"}
