"""Setup LifeSpan before the application starts."""

from contextlib import asynccontextmanager
from pathlib import Path

from app.feature.member.rep_member import MemberRepository
from app.service.watcher.srv_watcher import FileWatcher
from fastapi import FastAPI
from loguru import logger

# Module-level setup - clean separation from lifespan orchestration
MEMBER_YAML_PATH = Path("data/members.yaml")

# Initialize repository with path injection
member_repo = MemberRepository(file_path=MEMBER_YAML_PATH)

# Create watcher with callback to repo.reload - clean coupling!
member_watcher = FileWatcher(file_path=MEMBER_YAML_PATH, callback=member_repo.reload)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: RUF029
    """Application lifespan context manager - pure orchestration only."""
    logger.info("🚀 Starting application lifespan...")

    try:
        # Register repository to app state
        logger.info("Registering MemberRepository to app state")
        app.state.member_repo = member_repo
        logger.info("✅ MemberRepository registered successfully")

        # Start file watcher for data monitoring
        logger.info("Starting file watcher for member data hot reload")
        member_watcher.start()
        app.state.member_watcher = member_watcher
        logger.info("✅ File watcher started and registered to app state")

        logger.info("✅ Application startup completed successfully")

    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("🛑 Shutting down application...")

    try:
        if hasattr(app.state, "member_watcher"):
            member_watcher.stop()
            logger.info("✅ File watcher stopped successfully")
    except Exception as e:
        logger.error(f"❌ Failed to stop file watcher: {e}")

    logger.info("✅ Application shutdown completed")
