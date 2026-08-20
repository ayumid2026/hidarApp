from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import prices, alerts, reports, users

# Create database tables (in production, use Alembic migrations)
# This is a quick way to create tables for development
async def init_db():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Hidar API",
    description="Market Price Intelligence for Ethiopian Farmers & Traders",
    version="0.1.0"
)

# CORS middleware to allow your frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prices.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(users.router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Hidar API", "docs": "/docs"}
