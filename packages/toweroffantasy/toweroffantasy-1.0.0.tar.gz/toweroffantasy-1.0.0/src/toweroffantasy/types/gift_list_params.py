# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .langs_enum import LangsEnum

__all__ = ["GiftListParams"]


class GiftListParams(TypedDict, total=False):
    lang: LangsEnum
    """Language code"""

    limit: int
    """Items per page"""

    page: int
    """Page number"""
