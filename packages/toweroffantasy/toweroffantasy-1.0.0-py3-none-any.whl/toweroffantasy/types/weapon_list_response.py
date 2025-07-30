# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .assets import Assets
from .banner import Banner
from .element import Element
from .._models import BaseModel
from .category import Category
from .shatter_or_charge import ShatterOrCharge

__all__ = ["WeaponListResponse", "Data"]


class Data(BaseModel):
    id: str

    assets: Assets

    banners: List[Banner]

    banners_count: int

    category: Category

    charge: ShatterOrCharge

    element: Element

    is_fate: bool

    is_limited: bool

    is_warehouse: bool

    name: str

    quality: str

    rarity: str

    shatter: ShatterOrCharge

    imitation_id: Optional[str] = None

    suit_id: Optional[str] = None


class WeaponListResponse(BaseModel):
    data: List[Data]

    limit: int

    max_page: int

    page: int

    total_items: int
