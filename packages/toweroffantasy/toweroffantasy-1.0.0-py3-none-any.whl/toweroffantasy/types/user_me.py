# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["UserMe"]


class UserMe(BaseModel):
    id: int

    created_at: datetime

    email: str

    roles: List[Literal["ADMIN", "MODERATOR", "USER"]]

    username: str
