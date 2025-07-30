# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Banner"]


class Banner(BaseModel):
    id: str

    end_at: datetime

    final_rerun: bool

    imitation_id: str

    is_collab: bool

    is_rerun: bool

    limited_only: bool

    link: Optional[str] = None

    position: int

    start_at: datetime

    suit_id: Optional[str] = None

    weapon_id: str
