from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routes import prices, alerts, reports, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Hidar API",
    description="Market Price Intelligence for Ethiopian Farmers & Traders",
    version="0.1.0",
    lifespan=lifespan
)

# CORS - allow all origins for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prices.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Hidar API", "docs": "/docs"}
