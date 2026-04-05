class WtError(Exception):
    """Base exception for wt."""


class UserFacingError(WtError):
    """Validation error that should be shown directly to the user."""
