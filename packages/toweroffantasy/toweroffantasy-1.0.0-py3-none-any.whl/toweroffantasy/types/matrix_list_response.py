# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .suit_assets import SuitAssets

__all__ = ["MatrixListResponse", "Data", "DataMatriceAssets"]


class DataMatriceAssets(BaseModel):
    icon: str

    large_icon: str


class Data(BaseModel):
    id: str

    assets: SuitAssets

    imitation_id: Optional[str] = None

    matrice_assets: DataMatriceAssets

    matrice_name: str

    name: str

    quality: str

    rarity: str

    weapon_id: Optional[str] = None


class MatrixListResponse(BaseModel):
    data: List[Data]

    limit: int

    max_page: int

    page: int

    total_items: int
