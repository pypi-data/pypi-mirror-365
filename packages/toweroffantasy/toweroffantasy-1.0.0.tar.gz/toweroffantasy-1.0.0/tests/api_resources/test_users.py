# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import UserMe, UserRetrieveByIDResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_by_id(self, client: Toweroffantasy) -> None:
        user = client.users.retrieve_by_id(
            0,
        )
        assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_by_id(self, client: Toweroffantasy) -> None:
        response = client.users.with_raw_response.retrieve_by_id(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_by_id(self, client: Toweroffantasy) -> None:
        with client.users.with_streaming_response.retrieve_by_id(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_me(self, client: Toweroffantasy) -> None:
        user = client.users.retrieve_me()
        assert_matches_type(UserMe, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_me(self, client: Toweroffantasy) -> None:
        response = client.users.with_raw_response.retrieve_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserMe, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_me(self, client: Toweroffantasy) -> None:
        with client.users.with_streaming_response.retrieve_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserMe, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_by_id(self, async_client: AsyncToweroffantasy) -> None:
        user = await async_client.users.retrieve_by_id(
            0,
        )
        assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_by_id(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.users.with_raw_response.retrieve_by_id(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_by_id(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.users.with_streaming_response.retrieve_by_id(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserRetrieveByIDResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_me(self, async_client: AsyncToweroffantasy) -> None:
        user = await async_client.users.retrieve_me()
        assert_matches_type(UserMe, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_me(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.users.with_raw_response.retrieve_me()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserMe, user, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_me(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.users.with_streaming_response.retrieve_me() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserMe, user, path=["response"])

        assert cast(Any, response.is_closed) is True
