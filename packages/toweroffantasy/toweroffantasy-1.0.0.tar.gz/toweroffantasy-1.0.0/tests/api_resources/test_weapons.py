# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import (
    WeaponListResponse,
    WeaponRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWeapons:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Toweroffantasy) -> None:
        weapon = client.weapons.retrieve(
            weapon_id="weapon_id",
        )
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Toweroffantasy) -> None:
        weapon = client.weapons.retrieve(
            weapon_id="weapon_id",
            lang="de",
        )
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Toweroffantasy) -> None:
        response = client.weapons.with_raw_response.retrieve(
            weapon_id="weapon_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        weapon = response.parse()
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Toweroffantasy) -> None:
        with client.weapons.with_streaming_response.retrieve(
            weapon_id="weapon_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            weapon = response.parse()
            assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Toweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `weapon_id` but received ''"):
            client.weapons.with_raw_response.retrieve(
                weapon_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Toweroffantasy) -> None:
        weapon = client.weapons.list()
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Toweroffantasy) -> None:
        weapon = client.weapons.list(
            charge_tier="charge_tier",
            charge_value=1,
            exclude_categories=["string"],
            exclude_elements=["string"],
            exclude_ids=["string"],
            exclude_qualities=["string"],
            exclude_rarities=["string"],
            include_categories=["string"],
            include_elements=["string"],
            include_ids=["string"],
            include_qualities=["string"],
            include_rarities=["string"],
            is_fate=True,
            is_limited=True,
            is_warehouse=True,
            lang="de",
            limit=1,
            name="name",
            page=1,
            shatter_tier="shatter_tier",
            shatter_value=1,
        )
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Toweroffantasy) -> None:
        response = client.weapons.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        weapon = response.parse()
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Toweroffantasy) -> None:
        with client.weapons.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            weapon = response.parse()
            assert_matches_type(WeaponListResponse, weapon, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWeapons:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        weapon = await async_client.weapons.retrieve(
            weapon_id="weapon_id",
        )
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        weapon = await async_client.weapons.retrieve(
            weapon_id="weapon_id",
            lang="de",
        )
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.weapons.with_raw_response.retrieve(
            weapon_id="weapon_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        weapon = await response.parse()
        assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.weapons.with_streaming_response.retrieve(
            weapon_id="weapon_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            weapon = await response.parse()
            assert_matches_type(WeaponRetrieveResponse, weapon, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `weapon_id` but received ''"):
            await async_client.weapons.with_raw_response.retrieve(
                weapon_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncToweroffantasy) -> None:
        weapon = await async_client.weapons.list()
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        weapon = await async_client.weapons.list(
            charge_tier="charge_tier",
            charge_value=1,
            exclude_categories=["string"],
            exclude_elements=["string"],
            exclude_ids=["string"],
            exclude_qualities=["string"],
            exclude_rarities=["string"],
            include_categories=["string"],
            include_elements=["string"],
            include_ids=["string"],
            include_qualities=["string"],
            include_rarities=["string"],
            is_fate=True,
            is_limited=True,
            is_warehouse=True,
            lang="de",
            limit=1,
            name="name",
            page=1,
            shatter_tier="shatter_tier",
            shatter_value=1,
        )
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.weapons.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        weapon = await response.parse()
        assert_matches_type(WeaponListResponse, weapon, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.weapons.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            weapon = await response.parse()
            assert_matches_type(WeaponListResponse, weapon, path=["response"])

        assert cast(Any, response.is_closed) is True
