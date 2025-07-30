# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import (
    Banner,
    BannerListResponse,
    BannerRetrieveCurrentResponse,
)
from toweroffantasy._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBanners:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Toweroffantasy) -> None:
        banner = client.banners.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        )
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Toweroffantasy) -> None:
        banner = client.banners.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
            final_rerun=True,
            is_collab=True,
            is_rerun=True,
            limited_only=True,
            link="link",
            suit_id="suit_id",
        )
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Toweroffantasy) -> None:
        response = client.banners.with_raw_response.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = response.parse()
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Toweroffantasy) -> None:
        with client.banners.with_streaming_response.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = response.parse()
            assert_matches_type(Banner, banner, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Toweroffantasy) -> None:
        banner = client.banners.list()
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Toweroffantasy) -> None:
        banner = client.banners.list(
            end_at_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            end_at_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            exclude_ids=["string"],
            final_rerun=True,
            include_ids=["string"],
            is_collab=True,
            is_rerun=True,
            limit=1,
            limited_only=True,
            page=1,
            start_at_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_at_before=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Toweroffantasy) -> None:
        response = client.banners.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = response.parse()
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Toweroffantasy) -> None:
        with client.banners.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = response.parse()
            assert_matches_type(BannerListResponse, banner, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_current(self, client: Toweroffantasy) -> None:
        banner = client.banners.retrieve_current()
        assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_current(self, client: Toweroffantasy) -> None:
        response = client.banners.with_raw_response.retrieve_current()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = response.parse()
        assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_current(self, client: Toweroffantasy) -> None:
        with client.banners.with_streaming_response.retrieve_current() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = response.parse()
            assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBanners:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncToweroffantasy) -> None:
        banner = await async_client.banners.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        )
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        banner = await async_client.banners.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
            final_rerun=True,
            is_collab=True,
            is_rerun=True,
            limited_only=True,
            link="link",
            suit_id="suit_id",
        )
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.banners.with_raw_response.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = await response.parse()
        assert_matches_type(Banner, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.banners.with_streaming_response.create(
            end_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            imitation_id="imitation_id",
            start_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            weapon_id="weapon_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = await response.parse()
            assert_matches_type(Banner, banner, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncToweroffantasy) -> None:
        banner = await async_client.banners.list()
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        banner = await async_client.banners.list(
            end_at_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            end_at_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            exclude_ids=["string"],
            final_rerun=True,
            include_ids=["string"],
            is_collab=True,
            is_rerun=True,
            limit=1,
            limited_only=True,
            page=1,
            start_at_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            start_at_before=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.banners.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = await response.parse()
        assert_matches_type(BannerListResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.banners.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = await response.parse()
            assert_matches_type(BannerListResponse, banner, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_current(self, async_client: AsyncToweroffantasy) -> None:
        banner = await async_client.banners.retrieve_current()
        assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_current(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.banners.with_raw_response.retrieve_current()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        banner = await response.parse()
        assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_current(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.banners.with_streaming_response.retrieve_current() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            banner = await response.parse()
            assert_matches_type(BannerRetrieveCurrentResponse, banner, path=["response"])

        assert cast(Any, response.is_closed) is True
