# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict

from .langs_enum import LangsEnum

__all__ = ["MatrixListParams"]


class MatrixListParams(TypedDict, total=False):
    exclude_ids: Optional[List[str]]
    """Matrix id should not be one of"""

    include_ids: Optional[List[str]]
    """Matrix id should be one of"""

    lang: LangsEnum
    """Language code"""

    limit: int
    """Items per page"""

    page: int
    """Page number"""
