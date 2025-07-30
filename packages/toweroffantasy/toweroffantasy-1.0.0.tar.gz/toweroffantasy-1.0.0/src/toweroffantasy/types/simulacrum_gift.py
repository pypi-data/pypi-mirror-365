# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["SimulacrumGift", "BackgroundColor"]


class BackgroundColor(BaseModel):
    a: float

    b: float

    g: float

    hex: str

    r: float


class SimulacrumGift(BaseModel):
    id: str

    background_color: BackgroundColor

    name: str
