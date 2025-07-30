# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from toweroffantasy import Toweroffantasy, AsyncToweroffantasy
from toweroffantasy.types import (
    MatrixListResponse,
    MatrixRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMatrices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Toweroffantasy) -> None:
        matrix = client.matrices.retrieve(
            matrix_id="matrix_id",
        )
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Toweroffantasy) -> None:
        matrix = client.matrices.retrieve(
            matrix_id="matrix_id",
            lang="de",
        )
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Toweroffantasy) -> None:
        response = client.matrices.with_raw_response.retrieve(
            matrix_id="matrix_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matrix = response.parse()
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Toweroffantasy) -> None:
        with client.matrices.with_streaming_response.retrieve(
            matrix_id="matrix_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matrix = response.parse()
            assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Toweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `matrix_id` but received ''"):
            client.matrices.with_raw_response.retrieve(
                matrix_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Toweroffantasy) -> None:
        matrix = client.matrices.list()
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Toweroffantasy) -> None:
        matrix = client.matrices.list(
            exclude_ids=["string"],
            include_ids=["string"],
            lang="de",
            limit=1,
            page=1,
        )
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Toweroffantasy) -> None:
        response = client.matrices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matrix = response.parse()
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Toweroffantasy) -> None:
        with client.matrices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matrix = response.parse()
            assert_matches_type(MatrixListResponse, matrix, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMatrices:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        matrix = await async_client.matrices.retrieve(
            matrix_id="matrix_id",
        )
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        matrix = await async_client.matrices.retrieve(
            matrix_id="matrix_id",
            lang="de",
        )
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.matrices.with_raw_response.retrieve(
            matrix_id="matrix_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matrix = await response.parse()
        assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.matrices.with_streaming_response.retrieve(
            matrix_id="matrix_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matrix = await response.parse()
            assert_matches_type(MatrixRetrieveResponse, matrix, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncToweroffantasy) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `matrix_id` but received ''"):
            await async_client.matrices.with_raw_response.retrieve(
                matrix_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncToweroffantasy) -> None:
        matrix = await async_client.matrices.list()
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncToweroffantasy) -> None:
        matrix = await async_client.matrices.list(
            exclude_ids=["string"],
            include_ids=["string"],
            lang="de",
            limit=1,
            page=1,
        )
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncToweroffantasy) -> None:
        response = await async_client.matrices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matrix = await response.parse()
        assert_matches_type(MatrixListResponse, matrix, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncToweroffantasy) -> None:
        async with async_client.matrices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matrix = await response.parse()
            assert_matches_type(MatrixListResponse, matrix, path=["response"])

        assert cast(Any, response.is_closed) is True
