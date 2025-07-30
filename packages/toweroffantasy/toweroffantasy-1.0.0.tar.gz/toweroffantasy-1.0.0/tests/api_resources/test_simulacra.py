# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import (
    SimulacraListResponse,
    SimulacraRetrieveResponse,
    SimulacraLikedGiftsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSimulacra:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.retrieve(
            simulacrum_id="simulacrum_id",
        )
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.retrieve(
            simulacrum_id="simulacrum_id",
            lang="de",
        )
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Toweroffantasy) -> None:
        response = client.simulacra.with_raw_response.retrieve(
            simulacrum_id="simulacrum_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = response.parse()
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Toweroffantasy) -> None:
        with client.simulacra.with_streaming_response.retrieve(
            simulacrum_id="simulacrum_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = response.parse()
            assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Toweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `simulacrum_id` but received ''"):
            client.simulacra.with_raw_response.retrieve(
                simulacrum_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.list()
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.list(
            exclude_ids=["string"],
            exclude_rarities=["string"],
            exclude_sex=["string"],
            include_ids=["string"],
            include_rarities=["string"],
            include_sex=["string"],
            is_limited=True,
            lang="de",
            limit=1,
            name="name",
            no_weapon=True,
            page=1,
        )
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Toweroffantasy) -> None:
        response = client.simulacra.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = response.parse()
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Toweroffantasy) -> None:
        with client.simulacra.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = response.parse()
            assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_liked_gifts(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.liked_gifts(
            simulacrum_id="simulacrum_id",
        )
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_liked_gifts_with_all_params(self, client: Toweroffantasy) -> None:
        simulacra = client.simulacra.liked_gifts(
            simulacrum_id="simulacrum_id",
            lang="de",
        )
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_liked_gifts(self, client: Toweroffantasy) -> None:
        response = client.simulacra.with_raw_response.liked_gifts(
            simulacrum_id="simulacrum_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = response.parse()
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_liked_gifts(self, client: Toweroffantasy) -> None:
        with client.simulacra.with_streaming_response.liked_gifts(
            simulacrum_id="simulacrum_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = response.parse()
            assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_liked_gifts(self, client: Toweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `simulacrum_id` but received ''"):
            client.simulacra.with_raw_response.liked_gifts(
                simulacrum_id="",
            )


class TestAsyncSimulacra:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.retrieve(
            simulacrum_id="simulacrum_id",
        )
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.retrieve(
            simulacrum_id="simulacrum_id",
            lang="de",
        )
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.simulacra.with_raw_response.retrieve(
            simulacrum_id="simulacrum_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = await response.parse()
        assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.simulacra.with_streaming_response.retrieve(
            simulacrum_id="simulacrum_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = await response.parse()
            assert_matches_type(SimulacraRetrieveResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `simulacrum_id` but received ''"):
            await async_client.simulacra.with_raw_response.retrieve(
                simulacrum_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.list()
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.list(
            exclude_ids=["string"],
            exclude_rarities=["string"],
            exclude_sex=["string"],
            include_ids=["string"],
            include_rarities=["string"],
            include_sex=["string"],
            is_limited=True,
            lang="de",
            limit=1,
            name="name",
            no_weapon=True,
            page=1,
        )
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.simulacra.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = await response.parse()
        assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.simulacra.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = await response.parse()
            assert_matches_type(SimulacraListResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_liked_gifts(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.liked_gifts(
            simulacrum_id="simulacrum_id",
        )
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_liked_gifts_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        simulacra = await async_client.simulacra.liked_gifts(
            simulacrum_id="simulacrum_id",
            lang="de",
        )
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_liked_gifts(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.simulacra.with_raw_response.liked_gifts(
            simulacrum_id="simulacrum_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        simulacra = await response.parse()
        assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_liked_gifts(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.simulacra.with_streaming_response.liked_gifts(
            simulacrum_id="simulacrum_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            simulacra = await response.parse()
            assert_matches_type(SimulacraLikedGiftsResponse, simulacra, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_liked_gifts(self, async_client: AsyncToweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `simulacrum_id` but received ''"):
            await async_client.simulacra.with_raw_response.liked_gifts(
                simulacrum_id="",
            )
