# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel

__all__ = ["UserRetrieveByIDResponse"]


class UserRetrieveByIDResponse(BaseModel):
    id: int

    created_at: datetime

    username: str
