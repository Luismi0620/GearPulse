class NotFoundError(Exception):
    """Raised when a referenced entity does not exist. Maps to HTTP 404."""


class ConflictError(Exception):
    """Raised when an operation conflicts with existing state. Maps to HTTP 409."""
