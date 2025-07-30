# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .banner import Banner
from .._models import BaseModel
from .imitation_assets import ImitationAssets

__all__ = ["SimulacraListResponse", "Data"]


class Data(BaseModel):
    id: str

    assets: ImitationAssets

    banners: List[Banner]

    banners_count: int

    is_limited: bool

    name: str

    no_weapon: bool

    rarity: str

    sex: str

    suit_id: Optional[str] = None

    weapon_id: Optional[str] = None


class SimulacraListResponse(BaseModel):
    data: List[Data]

    limit: int

    max_page: int

    page: int

    total_items: int
