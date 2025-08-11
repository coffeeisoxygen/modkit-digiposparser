"""exceptions khusus untuk internal service atau api."""

from app.exceptions.custom.exc_base import BaseExcpError


class InternalServiceError(BaseExcpError):
    pass
