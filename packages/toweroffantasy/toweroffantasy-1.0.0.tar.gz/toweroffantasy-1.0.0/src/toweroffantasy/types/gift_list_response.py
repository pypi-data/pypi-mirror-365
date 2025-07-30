# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .gift import Gift
from .._models import BaseModel

__all__ = ["GiftListResponse"]


class GiftListResponse(BaseModel):
    data: List[Gift]

    limit: int

    max_page: int

    page: int

    total_items: int
