# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .banner import Banner
from .._models import BaseModel

__all__ = ["BannerListResponse"]


class BannerListResponse(BaseModel):
    data: List[Banner]

    limit: int

    max_page: int

    page: int

    total_items: int
