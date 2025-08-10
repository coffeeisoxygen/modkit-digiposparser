"""Setup LifeSpan before the application starts."""

from contextlib import asynccontextmanager
from pathlib import Path

from app.feature.member import MemberManager
from app.feature.member.srv_memberdata import reload_member_data
from app.service.watcher.srv_watcher import FileWatcher
from fastapi import FastAPI
from loguru import logger

MEMBER_YAML_PATH = Path("data/members.yaml")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager - orchestration only."""
    logger.info("🚀 Starting application lifespan...")

    try:
        app.state.member_manager = MemberManager()

        # 2. Initial data load
        members_dict, members_list = reload_member_data(MEMBER_YAML_PATH)
        app.state.member_manager.update_data(members_dict, members_list)

        # 3. Setup file watcher with proper callback
        def reload_callback():
            try:
                members_dict, members_list = reload_member_data(MEMBER_YAML_PATH)
                app.state.member_manager.update_data(members_dict, members_list)
                logger.info("🔄 Member data reloaded via file watcher")
            except Exception as e:
                logger.error("❌ Failed to reload member data", error=str(e))

        app.state.file_watcher = FileWatcher(MEMBER_YAML_PATH, reload_callback)
        app.state.file_watcher.start()

        logger.info("✅ Application startup completed")

    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

    yield  # Application runs here

    # Cleanup on shutdown
    logger.info("🛑 Shutting down application...")

    if hasattr(app.state, "file_watcher"):
        app.state.file_watcher.stop()
        logger.info("✅ File watcher stopped")

    logger.info("✅ Application shutdown completed")
