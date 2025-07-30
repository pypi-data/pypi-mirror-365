# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .banner import Banner
from .._models import BaseModel
from .suit_assets import SuitAssets
from .matrice_assets import MatriceAssets

__all__ = ["MatrixRetrieveResponse", "Matrix", "MatrixModifier", "MatrixModifierAssets", "Set"]


class MatrixModifierAssets(BaseModel):
    add_icon: Optional[str] = None

    dec_icon: Optional[str] = None

    icon: str


class MatrixModifier(BaseModel):
    id: str

    assets: MatrixModifierAssets

    description: str

    initial_value: float

    is_percentage: bool

    is_tag: bool

    is_uncommon: bool

    modifier_op: str

    modifier_value: float

    name: str


class Matrix(BaseModel):
    id: str

    assets: MatriceAssets

    base_exp: int

    description: str

    max_level: int

    max_star: int

    modifiers: List[MatrixModifier]

    name: str

    quality: str

    rarity: str

    slot_index: int

    suit_id: str


class Set(BaseModel):
    add_score: float

    description: str

    is_global: bool

    needs: int


class MatrixRetrieveResponse(BaseModel):
    id: str

    assets: SuitAssets

    banners: List[Banner]

    matrice_assets: MatriceAssets

    matrice_name: str

    matrices: List[Matrix]

    name: str

    quality: str

    rarity: str

    sets: List[Set]

    banners_count: Optional[int] = None

    imitation_id: Optional[str] = None

    weapon_id: Optional[str] = None
