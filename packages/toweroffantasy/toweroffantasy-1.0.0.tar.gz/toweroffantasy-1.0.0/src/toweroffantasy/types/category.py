# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Category"]


class Category(BaseModel):
    id: str

    icon: str

    icon_gray: str

    name: str
