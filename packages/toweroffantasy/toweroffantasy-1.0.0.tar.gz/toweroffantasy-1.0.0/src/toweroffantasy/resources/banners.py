# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime

import httpx

from ..types import banner_list_params, banner_create_params
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
from ..types.banner import Banner
from ..types.banner_list_response import BannerListResponse
from ..types.banner_retrieve_current_response import BannerRetrieveCurrentResponse

__all__ = ["BannersResource", "AsyncBannersResource"]


class BannersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BannersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return BannersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BannersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return BannersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        end_at: Union[str, datetime],
        imitation_id: str,
        start_at: Union[str, datetime],
        weapon_id: str,
        final_rerun: bool | NotGiven = NOT_GIVEN,
        is_collab: bool | NotGiven = NOT_GIVEN,
        is_rerun: bool | NotGiven = NOT_GIVEN,
        limited_only: bool | NotGiven = NOT_GIVEN,
        link: Optional[str] | NotGiven = NOT_GIVEN,
        suit_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Banner:
        """
        Create Banner

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/banners",
            body=maybe_transform(
                {
                    "end_at": end_at,
                    "imitation_id": imitation_id,
                    "start_at": start_at,
                    "weapon_id": weapon_id,
                    "final_rerun": final_rerun,
                    "is_collab": is_collab,
                    "is_rerun": is_rerun,
                    "limited_only": limited_only,
                    "link": link,
                    "suit_id": suit_id,
                },
                banner_create_params.BannerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Banner,
        )

    def list(
        self,
        *,
        end_at_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        end_at_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        final_rerun: Optional[bool] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        is_collab: Optional[bool] | NotGiven = NOT_GIVEN,
        is_rerun: Optional[bool] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        limited_only: Optional[bool] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        start_at_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        start_at_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BannerListResponse:
        """
        Get Banners

        Args:
          end_at_after: Filter banners that end after this date

          end_at_before: Filter banners that end before this date

          exclude_ids: Object ID should not be one of

          final_rerun: Filter banners that are final reruns

          include_ids: Object ID should be one of

          is_collab: Filter banners that are collaborations

          is_rerun: Filter banners that are reruns

          limit: Items per page

          limited_only: Filter banners that are limited only

          page: Page number

          start_at_after: Filter banners that start after this date

          start_at_before: Filter banners that start before this date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/banners",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_at_after": end_at_after,
                        "end_at_before": end_at_before,
                        "exclude_ids": exclude_ids,
                        "final_rerun": final_rerun,
                        "include_ids": include_ids,
                        "is_collab": is_collab,
                        "is_rerun": is_rerun,
                        "limit": limit,
                        "limited_only": limited_only,
                        "page": page,
                        "start_at_after": start_at_after,
                        "start_at_before": start_at_before,
                    },
                    banner_list_params.BannerListParams,
                ),
            ),
            cast_to=BannerListResponse,
        )

    def retrieve_current(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BannerRetrieveCurrentResponse:
        """Get Current Banners"""
        return self._get(
            "/banners/current",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BannerRetrieveCurrentResponse,
        )


class AsyncBannersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBannersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBannersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBannersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return AsyncBannersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        end_at: Union[str, datetime],
        imitation_id: str,
        start_at: Union[str, datetime],
        weapon_id: str,
        final_rerun: bool | NotGiven = NOT_GIVEN,
        is_collab: bool | NotGiven = NOT_GIVEN,
        is_rerun: bool | NotGiven = NOT_GIVEN,
        limited_only: bool | NotGiven = NOT_GIVEN,
        link: Optional[str] | NotGiven = NOT_GIVEN,
        suit_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Banner:
        """
        Create Banner

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/banners",
            body=await async_maybe_transform(
                {
                    "end_at": end_at,
                    "imitation_id": imitation_id,
                    "start_at": start_at,
                    "weapon_id": weapon_id,
                    "final_rerun": final_rerun,
                    "is_collab": is_collab,
                    "is_rerun": is_rerun,
                    "limited_only": limited_only,
                    "link": link,
                    "suit_id": suit_id,
                },
                banner_create_params.BannerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Banner,
        )

    async def list(
        self,
        *,
        end_at_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        end_at_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        final_rerun: Optional[bool] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        is_collab: Optional[bool] | NotGiven = NOT_GIVEN,
        is_rerun: Optional[bool] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        limited_only: Optional[bool] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        start_at_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        start_at_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BannerListResponse:
        """
        Get Banners

        Args:
          end_at_after: Filter banners that end after this date

          end_at_before: Filter banners that end before this date

          exclude_ids: Object ID should not be one of

          final_rerun: Filter banners that are final reruns

          include_ids: Object ID should be one of

          is_collab: Filter banners that are collaborations

          is_rerun: Filter banners that are reruns

          limit: Items per page

          limited_only: Filter banners that are limited only

          page: Page number

          start_at_after: Filter banners that start after this date

          start_at_before: Filter banners that start before this date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/banners",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_at_after": end_at_after,
                        "end_at_before": end_at_before,
                        "exclude_ids": exclude_ids,
                        "final_rerun": final_rerun,
                        "include_ids": include_ids,
                        "is_collab": is_collab,
                        "is_rerun": is_rerun,
                        "limit": limit,
                        "limited_only": limited_only,
                        "page": page,
                        "start_at_after": start_at_after,
                        "start_at_before": start_at_before,
                    },
                    banner_list_params.BannerListParams,
                ),
            ),
            cast_to=BannerListResponse,
        )

    async def retrieve_current(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BannerRetrieveCurrentResponse:
        """Get Current Banners"""
        return await self._get(
            "/banners/current",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BannerRetrieveCurrentResponse,
        )


class BannersResourceWithRawResponse:
    def __init__(self, banners: BannersResource) -> None:
        self._banners = banners

        self.create = to_raw_response_wrapper(
            banners.create,
        )
        self.list = to_raw_response_wrapper(
            banners.list,
        )
        self.retrieve_current = to_raw_response_wrapper(
            banners.retrieve_current,
        )


class AsyncBannersResourceWithRawResponse:
    def __init__(self, banners: AsyncBannersResource) -> None:
        self._banners = banners

        self.create = async_to_raw_response_wrapper(
            banners.create,
        )
        self.list = async_to_raw_response_wrapper(
            banners.list,
        )
        self.retrieve_current = async_to_raw_response_wrapper(
            banners.retrieve_current,
        )


class BannersResourceWithStreamingResponse:
    def __init__(self, banners: BannersResource) -> None:
        self._banners = banners

        self.create = to_streamed_response_wrapper(
            banners.create,
        )
        self.list = to_streamed_response_wrapper(
            banners.list,
        )
        self.retrieve_current = to_streamed_response_wrapper(
            banners.retrieve_current,
        )


class AsyncBannersResourceWithStreamingResponse:
    def __init__(self, banners: AsyncBannersResource) -> None:
        self._banners = banners

        self.create = async_to_streamed_response_wrapper(
            banners.create,
        )
        self.list = async_to_streamed_response_wrapper(
            banners.list,
        )
        self.retrieve_current = async_to_streamed_response_wrapper(
            banners.retrieve_current,
        )
