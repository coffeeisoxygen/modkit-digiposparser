"""Setup LifeSpan before the application starts."""

from contextlib import asynccontextmanager
from pathlib import Path

from app.feature.member import MemberManager
from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager - orchestration only."""
    logger.info("🚀 Starting application lifespan...")

    # Initialize member management
    yaml_path = Path("data/members.yaml")
    app.state.member_manager = MemberManager(yaml_path)

    try:
        # Initialize data and start watcher
        app.state.member_manager.initialize()
        app.state.member_manager.start_watcher()
        logger.info("✅ Member management started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start member management: {e}")
        raise

    logger.info("✅ Application startup completed")

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("🛑 Shutting down application...")

    if hasattr(app.state, "member_manager"):
        app.state.member_manager.stop_watcher()
        logger.info("✅ Member management stopped")

    logger.info("✅ Application shutdown completed")
