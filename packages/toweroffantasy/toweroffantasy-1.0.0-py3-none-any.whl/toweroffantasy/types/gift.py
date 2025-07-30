# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["Gift", "Assets"]


class Assets(BaseModel):
    icon: str


class Gift(BaseModel):
    id: str

    assets: Assets

    desc: str

    hobby_flag: List[str]

    name: str

    quality: str

    value: int
