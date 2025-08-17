from fastapi import FastAPI
import uvicorn
from src.routers.yahoo_stock_routes import router as yahoo_router
from src.config.settings import settings
from src.config.logging_config import get_logger, setup_logging

app = FastAPI(
    title="Stock Forecast API",
    description="A comprehensive API for stock data and forecasting",
    version="1.0.0"
)

# Include routers
app.include_router(yahoo_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

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