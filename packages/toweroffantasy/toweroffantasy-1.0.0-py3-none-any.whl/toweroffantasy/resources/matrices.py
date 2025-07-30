# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import LangsEnum, matrix_list_params, matrix_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.langs_enum import LangsEnum
from ..types.matrix_list_response import MatrixListResponse
from ..types.matrix_retrieve_response import MatrixRetrieveResponse

__all__ = ["MatricesResource", "AsyncMatricesResource"]


class MatricesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatricesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return MatricesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatricesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return MatricesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        matrix_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatrixRetrieveResponse:
        """
        Get Matrice

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not matrix_id:
            raise ValueError(f"Expected a non-empty value for `matrix_id` but received {matrix_id!r}")
        return self._get(
            f"/matrices/{matrix_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"lang": lang}, matrix_retrieve_params.MatrixRetrieveParams),
            ),
            cast_to=MatrixRetrieveResponse,
        )

    def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatrixListResponse:
        """
        Get All Matrice

        Args:
          exclude_ids: Matrix id should not be one of

          include_ids: Matrix id should be one of

          lang: Language code

          limit: Items per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/matrices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "include_ids": include_ids,
                        "lang": lang,
                        "limit": limit,
                        "page": page,
                    },
                    matrix_list_params.MatrixListParams,
                ),
            ),
            cast_to=MatrixListResponse,
        )


class AsyncMatricesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatricesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMatricesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatricesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return AsyncMatricesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        matrix_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatrixRetrieveResponse:
        """
        Get Matrice

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not matrix_id:
            raise ValueError(f"Expected a non-empty value for `matrix_id` but received {matrix_id!r}")
        return await self._get(
            f"/matrices/{matrix_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"lang": lang}, matrix_retrieve_params.MatrixRetrieveParams),
            ),
            cast_to=MatrixRetrieveResponse,
        )

    async def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MatrixListResponse:
        """
        Get All Matrice

        Args:
          exclude_ids: Matrix id should not be one of

          include_ids: Matrix id should be one of

          lang: Language code

          limit: Items per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/matrices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "include_ids": include_ids,
                        "lang": lang,
                        "limit": limit,
                        "page": page,
                    },
                    matrix_list_params.MatrixListParams,
                ),
            ),
            cast_to=MatrixListResponse,
        )


class MatricesResourceWithRawResponse:
    def __init__(self, matrices: MatricesResource) -> None:
        self._matrices = matrices

        self.retrieve = to_raw_response_wrapper(
            matrices.retrieve,
        )
        self.list = to_raw_response_wrapper(
            matrices.list,
        )


class AsyncMatricesResourceWithRawResponse:
    def __init__(self, matrices: AsyncMatricesResource) -> None:
        self._matrices = matrices

        self.retrieve = async_to_raw_response_wrapper(
            matrices.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            matrices.list,
        )


class MatricesResourceWithStreamingResponse:
    def __init__(self, matrices: MatricesResource) -> None:
        self._matrices = matrices

        self.retrieve = to_streamed_response_wrapper(
            matrices.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            matrices.list,
        )


class AsyncMatricesResourceWithStreamingResponse:
    def __init__(self, matrices: AsyncMatricesResource) -> None:
        self._matrices = matrices

        self.retrieve = async_to_streamed_response_wrapper(
            matrices.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            matrices.list,
        )
