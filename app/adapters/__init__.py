"""Response Adapters Package.

Provides adapter pattern implementation for flexible response formatting.
Supports both JSON (FastAPI standard) and Plaintext (Otomax requirement).
"""

from app.adapters.response_adapter import (
    JsonResponseAdapter,
    PlaintextResponseAdapter,
    ResponseAdapter,
)

__all__ = [
    "JsonResponseAdapter",
    "PlaintextResponseAdapter",
    "ResponseAdapter",
]
