from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `toweroffantasy.resources` module.

    This is used so that we can lazily import `toweroffantasy.resources` only when
    needed *and* so that users can just import `toweroffantasy` and reference `toweroffantasy.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("toweroffantasy.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
