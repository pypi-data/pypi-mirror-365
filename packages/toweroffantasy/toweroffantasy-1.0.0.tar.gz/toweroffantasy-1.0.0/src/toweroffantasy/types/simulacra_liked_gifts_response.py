# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .gift import Gift

__all__ = ["SimulacraLikedGiftsResponse"]

SimulacraLikedGiftsResponse: TypeAlias = List[Gift]
