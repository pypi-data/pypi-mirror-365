# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import Gift, GiftListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGifts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Toweroffantasy) -> None:
        gift = client.gifts.retrieve(
            gift_id="gift_id",
        )
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Toweroffantasy) -> None:
        gift = client.gifts.retrieve(
            gift_id="gift_id",
            lang="de",
        )
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Toweroffantasy) -> None:
        response = client.gifts.with_raw_response.retrieve(
            gift_id="gift_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        gift = response.parse()
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Toweroffantasy) -> None:
        with client.gifts.with_streaming_response.retrieve(
            gift_id="gift_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            gift = response.parse()
            assert_matches_type(Gift, gift, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Toweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `gift_id` but received ''"):
            client.gifts.with_raw_response.retrieve(
                gift_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Toweroffantasy) -> None:
        gift = client.gifts.list()
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Toweroffantasy) -> None:
        gift = client.gifts.list(
            lang="de",
            limit=1,
            page=1,
        )
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Toweroffantasy) -> None:
        response = client.gifts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        gift = response.parse()
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Toweroffantasy) -> None:
        with client.gifts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            gift = response.parse()
            assert_matches_type(GiftListResponse, gift, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGifts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        gift = await async_client.gifts.retrieve(
            gift_id="gift_id",
        )
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        gift = await async_client.gifts.retrieve(
            gift_id="gift_id",
            lang="de",
        )
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.gifts.with_raw_response.retrieve(
            gift_id="gift_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        gift = await response.parse()
        assert_matches_type(Gift, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.gifts.with_streaming_response.retrieve(
            gift_id="gift_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            gift = await response.parse()
            assert_matches_type(Gift, gift, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `gift_id` but received ''"):
            await async_client.gifts.with_raw_response.retrieve(
                gift_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncToweroffantasy) -> None:
        gift = await async_client.gifts.list()
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        gift = await async_client.gifts.list(
            lang="de",
            limit=1,
            page=1,
        )
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.gifts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        gift = await response.parse()
        assert_matches_type(GiftListResponse, gift, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.gifts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            gift = await response.parse()
            assert_matches_type(GiftListResponse, gift, path=["response"])

        assert cast(Any, response.is_closed) is True
