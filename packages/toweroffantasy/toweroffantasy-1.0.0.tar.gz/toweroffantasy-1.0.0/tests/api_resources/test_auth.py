# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import LoginResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_change_password(self, client: Toweroffantasy) -> None:
        auth = client.auth.change_password(
            new_password="new_password",
            old_password="old_password",
        )
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_change_password(self, client: Toweroffantasy) -> None:
        response = client.auth.with_raw_response.change_password(
            new_password="new_password",
            old_password="old_password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_change_password(self, client: Toweroffantasy) -> None:
        with client.auth.with_streaming_response.change_password(
            new_password="new_password",
            old_password="old_password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_check_access_token(self, client: Toweroffantasy) -> None:
        auth = client.auth.check_access_token()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_check_access_token(self, client: Toweroffantasy) -> None:
        response = client.auth.with_raw_response.check_access_token()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_check_access_token(self, client: Toweroffantasy) -> None:
        with client.auth.with_streaming_response.check_access_token() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(object, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_login(self, client: Toweroffantasy) -> None:
        auth = client.auth.login(
            email="email",
            password="password",
        )
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_login(self, client: Toweroffantasy) -> None:
        response = client.auth.with_raw_response.login(
            email="email",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_login(self, client: Toweroffantasy) -> None:
        with client.auth.with_streaming_response.login(
            email="email",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(LoginResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_register(self, client: Toweroffantasy) -> None:
        auth = client.auth.register(
            email="email",
            password="password",
            username="username",
        )
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_register(self, client: Toweroffantasy) -> None:
        response = client.auth.with_raw_response.register(
            email="email",
            password="password",
            username="username",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_register(self, client: Toweroffantasy) -> None:
        with client.auth.with_streaming_response.register(
            email="email",
            password="password",
            username="username",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(LoginResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_change_password(self, async_client: AsyncToweroffantasy) -> None:
        auth = await async_client.auth.change_password(
            new_password="new_password",
            old_password="old_password",
        )
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_change_password(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.auth.with_raw_response.change_password(
            new_password="new_password",
            old_password="old_password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert auth is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_change_password(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.auth.with_streaming_response.change_password(
            new_password="new_password",
            old_password="old_password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert auth is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_check_access_token(self, async_client: AsyncToweroffantasy) -> None:
        auth = await async_client.auth.check_access_token()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_check_access_token(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.auth.with_raw_response.check_access_token()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(object, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_check_access_token(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.auth.with_streaming_response.check_access_token() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(object, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_login(self, async_client: AsyncToweroffantasy) -> None:
        auth = await async_client.auth.login(
            email="email",
            password="password",
        )
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_login(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.auth.with_raw_response.login(
            email="email",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_login(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.auth.with_streaming_response.login(
            email="email",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(LoginResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_register(self, async_client: AsyncToweroffantasy) -> None:
        auth = await async_client.auth.register(
            email="email",
            password="password",
            username="username",
        )
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_register(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.auth.with_raw_response.register(
            email="email",
            password="password",
            username="username",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(LoginResponse, auth, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_register(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.auth.with_streaming_response.register(
            email="email",
            password="password",
            username="username",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(LoginResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
