"""Setup LifeSpan before the application starts."""

from contextlib import asynccontextmanager
from pathlib import Path

from app.feature.member import MemberManager
from app.service.watcher.srv_watcher import FileWatcher
from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("🚀 Starting application lifespan...")

    # Initialize member management
    yaml_path = Path("tests/.sample/test_members.yaml")  # Use test data for now

    # Create and initialize member manager
    app.state.member_manager = MemberManager(yaml_path)
    try:
        app.state.member_manager.initialize()
        logger.info("✅ Member manager initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize member manager: {e}")
        raise

    # Setup file watcher for hot reload
    def reload_callback():
        """Callback function for file watcher."""
        try:
            app.state.member_manager.reload()
            logger.info("🔄 Member data reloaded due to file change")
        except Exception as e:
            logger.error(f"❌ Failed to reload member data: {e}")

    app.state.file_watcher = FileWatcher(yaml_path, reload_callback)
    app.state.file_watcher.start()
    logger.info("👁️ File watcher started for member data hot reload")

    logger.info("✅ Application startup completed")

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("🛑 Shutting down application...")

    if hasattr(app.state, "file_watcher"):
        app.state.file_watcher.stop()
        logger.info("👁️ File watcher stopped")

    logger.info("✅ Application shutdown completed")
