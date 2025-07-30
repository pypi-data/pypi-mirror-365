# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Element"]


class Element(BaseModel):
    id: str

    desc: str

    icon: str

    name: str
