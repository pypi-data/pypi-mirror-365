# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .langs_enum import LangsEnum

__all__ = ["WeaponRetrieveParams"]


class WeaponRetrieveParams(TypedDict, total=False):
    lang: LangsEnum
