# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import LangsEnum, gift_list_params, gift_retrieve_params
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
from ..types.gift import Gift
from .._base_client import make_request_options
from ..types.langs_enum import LangsEnum
from ..types.gift_list_response import GiftListResponse

__all__ = ["GiftsResource", "AsyncGiftsResource"]


class GiftsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GiftsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return GiftsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GiftsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return GiftsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        gift_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Gift:
        """
        Get Gift

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not gift_id:
            raise ValueError(f"Expected a non-empty value for `gift_id` but received {gift_id!r}")
        return self._get(
            f"/gifts/{gift_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"lang": lang}, gift_retrieve_params.GiftRetrieveParams),
            ),
            cast_to=Gift,
        )

    def list(
        self,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GiftListResponse:
        """
        Get All Gifts

        Args:
          lang: Language code

          limit: Items per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/gifts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "lang": lang,
                        "limit": limit,
                        "page": page,
                    },
                    gift_list_params.GiftListParams,
                ),
            ),
            cast_to=GiftListResponse,
        )


class AsyncGiftsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGiftsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncGiftsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGiftsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return AsyncGiftsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        gift_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Gift:
        """
        Get Gift

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not gift_id:
            raise ValueError(f"Expected a non-empty value for `gift_id` but received {gift_id!r}")
        return await self._get(
            f"/gifts/{gift_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"lang": lang}, gift_retrieve_params.GiftRetrieveParams),
            ),
            cast_to=Gift,
        )

    async def list(
        self,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GiftListResponse:
        """
        Get All Gifts

        Args:
          lang: Language code

          limit: Items per page

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/gifts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "lang": lang,
                        "limit": limit,
                        "page": page,
                    },
                    gift_list_params.GiftListParams,
                ),
            ),
            cast_to=GiftListResponse,
        )


class GiftsResourceWithRawResponse:
    def __init__(self, gifts: GiftsResource) -> None:
        self._gifts = gifts

        self.retrieve = to_raw_response_wrapper(
            gifts.retrieve,
        )
        self.list = to_raw_response_wrapper(
            gifts.list,
        )


class AsyncGiftsResourceWithRawResponse:
    def __init__(self, gifts: AsyncGiftsResource) -> None:
        self._gifts = gifts

        self.retrieve = async_to_raw_response_wrapper(
            gifts.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            gifts.list,
        )


class GiftsResourceWithStreamingResponse:
    def __init__(self, gifts: GiftsResource) -> None:
        self._gifts = gifts

        self.retrieve = to_streamed_response_wrapper(
            gifts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            gifts.list,
        )


class AsyncGiftsResourceWithStreamingResponse:
    def __init__(self, gifts: AsyncGiftsResource) -> None:
        self._gifts = gifts

        self.retrieve = async_to_streamed_response_wrapper(
            gifts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            gifts.list,
        )
