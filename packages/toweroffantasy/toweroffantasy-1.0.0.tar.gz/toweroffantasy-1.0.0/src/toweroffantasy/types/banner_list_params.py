# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BannerListParams"]


class BannerListParams(TypedDict, total=False):
    end_at_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter banners that end after this date"""

    end_at_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter banners that end before this date"""

    exclude_ids: Optional[List[str]]
    """Object ID should not be one of"""

    final_rerun: Optional[bool]
    """Filter banners that are final reruns"""

    include_ids: Optional[List[str]]
    """Object ID should be one of"""

    is_collab: Optional[bool]
    """Filter banners that are collaborations"""

    is_rerun: Optional[bool]
    """Filter banners that are reruns"""

    limit: int
    """Items per page"""

    limited_only: Optional[bool]
    """Filter banners that are limited only"""

    page: int
    """Page number"""

    start_at_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter banners that start after this date"""

    start_at_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter banners that start before this date"""
