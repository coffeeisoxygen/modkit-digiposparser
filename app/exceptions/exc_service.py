"""exceptions khusus untuk internal service atau api."""

from app.exceptions.exc_base import BaseExcpError


class InternalServiceError(BaseExcpError):
    pass
