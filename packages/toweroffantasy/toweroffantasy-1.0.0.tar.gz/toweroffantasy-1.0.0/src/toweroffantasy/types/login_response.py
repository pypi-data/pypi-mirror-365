# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .user_me import UserMe
from .._models import BaseModel

__all__ = ["LoginResponse"]


class LoginResponse(BaseModel):
    access_expire: datetime

    access_token: str

    refresh_token: str

    user: UserMe
    """Data Transfer Object for exporting the current user."""
