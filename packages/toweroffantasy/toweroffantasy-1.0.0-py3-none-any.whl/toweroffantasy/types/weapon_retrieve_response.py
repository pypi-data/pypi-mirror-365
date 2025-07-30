# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .assets import Assets
from .banner import Banner
from .element import Element
from .._models import BaseModel
from .category import Category
from .shatter_or_charge import ShatterOrCharge

__all__ = [
    "WeaponRetrieveResponse",
    "Advancement",
    "AdvancementAttribute",
    "AdvancementNeedItem",
    "Fashion",
    "MultiElement",
    "RecommendedMatrix",
    "Skill",
    "SkillAttack",
    "SkillAttackTag",
]


class AdvancementAttribute(BaseModel):
    id: str

    value: float


class AdvancementNeedItem(BaseModel):
    id: str

    count: int


class Advancement(BaseModel):
    attributes: List[AdvancementAttribute]

    charge: ShatterOrCharge

    cost_type: str

    desc: str

    need_golds: int

    need_item: AdvancementNeedItem

    shatter: ShatterOrCharge

    star_skill_score: int


class Fashion(BaseModel):
    id: str

    brief: str

    desc: str

    display_type_text: str

    icon: str

    name: str

    quality: str

    use_desc: str


class MultiElement(BaseModel):
    element: str

    passives: List[str]


class RecommendedMatrix(BaseModel):
    id: str

    reason: str


class SkillAttackTag(BaseModel):
    id: str

    name: str


class SkillAttack(BaseModel):
    id: str

    desc: str

    icon: str

    name: str

    operations: List[str]

    short_desc: Optional[str] = None

    tags: List[SkillAttackTag]

    values: List[List[float]]


class Skill(BaseModel):
    attacks: List[SkillAttack]

    desc: Optional[str] = None

    icon: str

    name: Optional[str] = None

    type: str


class WeaponRetrieveResponse(BaseModel):
    id: str

    assets: Assets

    banners: List[Banner]

    banners_count: int

    brief: str

    category: Category

    charge: ShatterOrCharge

    desc: str

    element: Element

    is_fate: bool

    is_limited: bool

    is_warehouse: bool

    lottery_desc: str

    name: str

    quality: str

    rarity: str

    shatter: ShatterOrCharge

    advancements: Optional[List[Advancement]] = None

    fashions: Optional[List[Fashion]] = None

    imitation_id: Optional[str] = None

    multi_element: Optional[List[MultiElement]] = None

    passives: Optional[List[str]] = None

    recommended_matrices: Optional[List[RecommendedMatrix]] = None

    skills: Optional[List[Skill]] = None

    suit_id: Optional[str] = None
