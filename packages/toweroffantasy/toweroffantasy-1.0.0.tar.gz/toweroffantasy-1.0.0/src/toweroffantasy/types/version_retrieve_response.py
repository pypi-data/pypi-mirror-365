# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["VersionRetrieveResponse"]


class VersionRetrieveResponse(BaseModel):
    api_version: Optional[str] = None

    game_version: Optional[str] = None
