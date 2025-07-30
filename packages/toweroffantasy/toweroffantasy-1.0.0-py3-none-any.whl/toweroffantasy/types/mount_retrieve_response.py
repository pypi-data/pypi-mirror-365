# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .mount_assets import MountAssets

__all__ = ["MountRetrieveResponse", "Skin"]


class Skin(BaseModel):
    id: str

    assets: MountAssets

    desc: str

    name: str

    owner_mount_id: str

    unlock_desc: str


class MountRetrieveResponse(BaseModel):
    id: str

    assets: MountAssets

    desc: str

    mount_type: str

    name: str

    quality: str

    skins: List[Skin]

    unlock_desc: str
