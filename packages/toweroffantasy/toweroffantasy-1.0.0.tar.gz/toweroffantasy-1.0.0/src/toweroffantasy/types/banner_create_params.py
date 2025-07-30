# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BannerCreateParams"]


class BannerCreateParams(TypedDict, total=False):
    end_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    imitation_id: Required[str]

    start_at: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    weapon_id: Required[str]

    final_rerun: bool

    is_collab: bool

    is_rerun: bool

    limited_only: bool

    link: Optional[str]

    suit_id: Optional[str]
