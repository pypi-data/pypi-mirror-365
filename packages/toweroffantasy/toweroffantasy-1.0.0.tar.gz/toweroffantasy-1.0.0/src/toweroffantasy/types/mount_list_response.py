# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .mount_assets import MountAssets

__all__ = ["MountListResponse", "Data"]


class Data(BaseModel):
    id: str

    assets: MountAssets

    mount_type: str

    name: str

    quality: str


class MountListResponse(BaseModel):
    data: List[Data]

    limit: int

    max_page: int

    page: int

    total_items: int
