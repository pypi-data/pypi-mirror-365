# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .banner import Banner
from .._models import BaseModel
from .simulacrum_gift import SimulacrumGift
from .imitation_assets import ImitationAssets

__all__ = [
    "SimulacraRetrieveResponse",
    "Extras",
    "ExtrasVoiceActors",
    "Fashion",
    "FashionAssets",
    "Likeability",
    "LikeabilityCondition",
    "LikeabilityModifier",
]


class ExtrasVoiceActors(BaseModel):
    chinese: Optional[str] = None

    english: Optional[str] = None

    japanese: Optional[str] = None

    korean: Optional[str] = None

    portuguese: Optional[str] = None


class Extras(BaseModel):
    age: str

    belong_to: Optional[str] = None

    birthday: Optional[str] = None

    character: Optional[str] = None

    dislike: List[SimulacrumGift]

    experience_record: Optional[str] = None

    gender: Optional[str] = None

    height: Optional[str] = None

    hometown: Optional[str] = None

    hometown_map: Optional[str] = None

    job: str

    like: List[SimulacrumGift]

    title: str

    voice_actors: ExtrasVoiceActors


class FashionAssets(BaseModel):
    gray_painting: str

    painting: str


class Fashion(BaseModel):
    id: str

    assets: FashionAssets

    desc: str

    imitation_id: str

    name: str

    only_weapon: bool

    quality: str

    source: str


class LikeabilityCondition(BaseModel):
    desc: str

    icon: str

    name: str

    quality: str

    use_desc: str


class LikeabilityModifier(BaseModel):
    id: str

    desc: str

    icon: str

    name: str

    operator: str

    value: float


class Likeability(BaseModel):
    big_icon: Optional[str] = None

    condition: int

    conditions: List[LikeabilityCondition]

    context: Optional[str] = None

    desc: Optional[str] = None

    icon: Optional[str] = None

    modifiers: List[LikeabilityModifier]

    name: Optional[str] = None

    type: str

    unlock_desc: Optional[str] = None


class SimulacraRetrieveResponse(BaseModel):
    id: str

    assets: ImitationAssets

    assets_a3: ImitationAssets

    avatar_id: str

    banners: List[Banner]

    banners_count: int

    desc: str

    extras: Extras

    fashions: List[Fashion]

    is_limited: bool

    likeabilities: List[Likeability]

    name: str

    no_weapon: bool

    rarity: str

    sex: str

    suit_id: Optional[str] = None

    unlock_info: str

    weapon_id: Optional[str] = None
