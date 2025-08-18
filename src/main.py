from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
from contextlib import asynccontextmanager
from src.database.connection import close_db, init_db
from src.routers.yahoo_stock_routes import router as yahoo_router
from src.routers.sync_stock_routers import router as sync_stock_router
from src.routers.stock_viewer_routers import router as stock_viewer_router
from src.config.settings import settings
from src.config.logging_config import get_logger, setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Setup logging first
    setup_logging()
    logger = get_logger(__name__)
    
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise here to allow the app to start even if DB is not available
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close database connections
    try:
        close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
    
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Stock Forecast API",
    description="A comprehensive API for stock data and forecasting",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(yahoo_router)
app.include_router(sync_stock_router)
app.include_router(stock_viewer_router)

@app.get("/")
async def root():
    return RedirectResponse(url="/stock-viewer")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Stock Forecast API is running"}

if __name__ == "__main__":
    """Main function to start the FastAPI application"""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting Stock Forecast API")

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )