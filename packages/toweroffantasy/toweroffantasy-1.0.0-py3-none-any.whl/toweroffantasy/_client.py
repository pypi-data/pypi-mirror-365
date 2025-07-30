# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import auth, ping, gifts, users, health, mounts, banners, version, weapons, matrices, simulacra
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, ToweroffantasyError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Toweroffantasy",
    "AsyncToweroffantasy",
    "Client",
    "AsyncClient",
]


class Toweroffantasy(SyncAPIClient):
    auth: auth.AuthResource
    users: users.UsersResource
    simulacra: simulacra.SimulacraResource
    matrices: matrices.MatricesResource
    weapons: weapons.WeaponsResource
    banners: banners.BannersResource
    gifts: gifts.GiftsResource
    mounts: mounts.MountsResource
    health: health.HealthResource
    ping: ping.PingResource
    version: version.VersionResource
    with_raw_response: ToweroffantasyWithRawResponse
    with_streaming_response: ToweroffantasyWithStreamedResponse

    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Toweroffantasy client instance.

        This automatically infers the `bearer_token` argument from the `TOWEROFFANTASY_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("TOWEROFFANTASY_BEARER_TOKEN")
        if bearer_token is None:
            raise ToweroffantasyError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the TOWEROFFANTASY_BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("TOWEROFFANTASY_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AuthResource(self)
        self.users = users.UsersResource(self)
        self.simulacra = simulacra.SimulacraResource(self)
        self.matrices = matrices.MatricesResource(self)
        self.weapons = weapons.WeaponsResource(self)
        self.banners = banners.BannersResource(self)
        self.gifts = gifts.GiftsResource(self)
        self.mounts = mounts.MountsResource(self)
        self.health = health.HealthResource(self)
        self.ping = ping.PingResource(self)
        self.version = version.VersionResource(self)
        self.with_raw_response = ToweroffantasyWithRawResponse(self)
        self.with_streaming_response = ToweroffantasyWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": bearer_token}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncToweroffantasy(AsyncAPIClient):
    auth: auth.AsyncAuthResource
    users: users.AsyncUsersResource
    simulacra: simulacra.AsyncSimulacraResource
    matrices: matrices.AsyncMatricesResource
    weapons: weapons.AsyncWeaponsResource
    banners: banners.AsyncBannersResource
    gifts: gifts.AsyncGiftsResource
    mounts: mounts.AsyncMountsResource
    health: health.AsyncHealthResource
    ping: ping.AsyncPingResource
    version: version.AsyncVersionResource
    with_raw_response: AsyncToweroffantasyWithRawResponse
    with_streaming_response: AsyncToweroffantasyWithStreamedResponse

    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncToweroffantasy client instance.

        This automatically infers the `bearer_token` argument from the `TOWEROFFANTASY_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("TOWEROFFANTASY_BEARER_TOKEN")
        if bearer_token is None:
            raise ToweroffantasyError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the TOWEROFFANTASY_BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("TOWEROFFANTASY_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AsyncAuthResource(self)
        self.users = users.AsyncUsersResource(self)
        self.simulacra = simulacra.AsyncSimulacraResource(self)
        self.matrices = matrices.AsyncMatricesResource(self)
        self.weapons = weapons.AsyncWeaponsResource(self)
        self.banners = banners.AsyncBannersResource(self)
        self.gifts = gifts.AsyncGiftsResource(self)
        self.mounts = mounts.AsyncMountsResource(self)
        self.health = health.AsyncHealthResource(self)
        self.ping = ping.AsyncPingResource(self)
        self.version = version.AsyncVersionResource(self)
        self.with_raw_response = AsyncToweroffantasyWithRawResponse(self)
        self.with_streaming_response = AsyncToweroffantasyWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": bearer_token}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class ToweroffantasyWithRawResponse:
    def __init__(self, client: Toweroffantasy) -> None:
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.simulacra = simulacra.SimulacraResourceWithRawResponse(client.simulacra)
        self.matrices = matrices.MatricesResourceWithRawResponse(client.matrices)
        self.weapons = weapons.WeaponsResourceWithRawResponse(client.weapons)
        self.banners = banners.BannersResourceWithRawResponse(client.banners)
        self.gifts = gifts.GiftsResourceWithRawResponse(client.gifts)
        self.mounts = mounts.MountsResourceWithRawResponse(client.mounts)
        self.health = health.HealthResourceWithRawResponse(client.health)
        self.ping = ping.PingResourceWithRawResponse(client.ping)
        self.version = version.VersionResourceWithRawResponse(client.version)


class AsyncToweroffantasyWithRawResponse:
    def __init__(self, client: AsyncToweroffantasy) -> None:
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.simulacra = simulacra.AsyncSimulacraResourceWithRawResponse(client.simulacra)
        self.matrices = matrices.AsyncMatricesResourceWithRawResponse(client.matrices)
        self.weapons = weapons.AsyncWeaponsResourceWithRawResponse(client.weapons)
        self.banners = banners.AsyncBannersResourceWithRawResponse(client.banners)
        self.gifts = gifts.AsyncGiftsResourceWithRawResponse(client.gifts)
        self.mounts = mounts.AsyncMountsResourceWithRawResponse(client.mounts)
        self.health = health.AsyncHealthResourceWithRawResponse(client.health)
        self.ping = ping.AsyncPingResourceWithRawResponse(client.ping)
        self.version = version.AsyncVersionResourceWithRawResponse(client.version)


class ToweroffantasyWithStreamedResponse:
    def __init__(self, client: Toweroffantasy) -> None:
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.simulacra = simulacra.SimulacraResourceWithStreamingResponse(client.simulacra)
        self.matrices = matrices.MatricesResourceWithStreamingResponse(client.matrices)
        self.weapons = weapons.WeaponsResourceWithStreamingResponse(client.weapons)
        self.banners = banners.BannersResourceWithStreamingResponse(client.banners)
        self.gifts = gifts.GiftsResourceWithStreamingResponse(client.gifts)
        self.mounts = mounts.MountsResourceWithStreamingResponse(client.mounts)
        self.health = health.HealthResourceWithStreamingResponse(client.health)
        self.ping = ping.PingResourceWithStreamingResponse(client.ping)
        self.version = version.VersionResourceWithStreamingResponse(client.version)


class AsyncToweroffantasyWithStreamedResponse:
    def __init__(self, client: AsyncToweroffantasy) -> None:
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.simulacra = simulacra.AsyncSimulacraResourceWithStreamingResponse(client.simulacra)
        self.matrices = matrices.AsyncMatricesResourceWithStreamingResponse(client.matrices)
        self.weapons = weapons.AsyncWeaponsResourceWithStreamingResponse(client.weapons)
        self.banners = banners.AsyncBannersResourceWithStreamingResponse(client.banners)
        self.gifts = gifts.AsyncGiftsResourceWithStreamingResponse(client.gifts)
        self.mounts = mounts.AsyncMountsResourceWithStreamingResponse(client.mounts)
        self.health = health.AsyncHealthResourceWithStreamingResponse(client.health)
        self.ping = ping.AsyncPingResourceWithStreamingResponse(client.ping)
        self.version = version.AsyncVersionResourceWithStreamingResponse(client.version)


Client = Toweroffantasy

AsyncClient = AsyncToweroffantasy
