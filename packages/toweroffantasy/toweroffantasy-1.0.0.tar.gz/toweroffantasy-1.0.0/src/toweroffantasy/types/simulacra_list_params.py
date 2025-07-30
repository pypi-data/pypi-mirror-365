# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict

from .langs_enum import LangsEnum

__all__ = ["SimulacraListParams"]


class SimulacraListParams(TypedDict, total=False):
    exclude_ids: Optional[List[str]]
    """Id should not be one of"""

    exclude_rarities: Optional[List[str]]
    """Rarity should exclude one of"""

    exclude_sex: Optional[List[str]]
    """Sex should exclude one of"""

    include_ids: Optional[List[str]]
    """Id should be one of"""

    include_rarities: Optional[List[str]]
    """Rarity should include one of"""

    include_sex: Optional[List[str]]
    """Sex should include one of"""

    is_limited: Optional[bool]
    """Is limited weapon (Red Nucleous)"""

    lang: LangsEnum
    """Language code"""

    limit: int
    """Items per page"""

    name: Optional[str]
    """Name should be part of"""

    no_weapon: Optional[bool]
    """No weapon (Polymorph)"""

    page: int
    """Page number"""
