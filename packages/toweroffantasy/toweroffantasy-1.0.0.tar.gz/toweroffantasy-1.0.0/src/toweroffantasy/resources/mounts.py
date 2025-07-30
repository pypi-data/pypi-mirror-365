# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import LangsEnum, mount_list_params, mount_retrieve_params
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
from ..types.mount_list_response import MountListResponse
from ..types.mount_retrieve_response import MountRetrieveResponse

__all__ = ["MountsResource", "AsyncMountsResource"]


class MountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return MountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return MountsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        mount_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MountRetrieveResponse:
        """
        Get Mount

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not mount_id:
            raise ValueError(f"Expected a non-empty value for `mount_id` but received {mount_id!r}")
        return self._get(
            f"/mounts/{mount_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"lang": lang}, mount_retrieve_params.MountRetrieveParams),
            ),
            cast_to=MountRetrieveResponse,
        )

    def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_mount_type: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_quality: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_mount_type: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_quality: Optional[List[str]] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MountListResponse:
        """
        Get Mounts

        Args:
          exclude_ids: Id should not be one of

          exclude_mount_type: Mount type should exclude one of

          exclude_quality: Quality should exclude one of

          include_ids: Id should be one of

          include_mount_type: Mount type should include one of

          include_quality: Quality should include one of

          lang: Language code

          limit: Items per page

          name: Name should be part of

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/mounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "exclude_mount_type": exclude_mount_type,
                        "exclude_quality": exclude_quality,
                        "include_ids": include_ids,
                        "include_mount_type": include_mount_type,
                        "include_quality": include_quality,
                        "lang": lang,
                        "limit": limit,
                        "name": name,
                        "page": page,
                    },
                    mount_list_params.MountListParams,
                ),
            ),
            cast_to=MountListResponse,
        )


class AsyncMountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return AsyncMountsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        mount_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MountRetrieveResponse:
        """
        Get Mount

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not mount_id:
            raise ValueError(f"Expected a non-empty value for `mount_id` but received {mount_id!r}")
        return await self._get(
            f"/mounts/{mount_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"lang": lang}, mount_retrieve_params.MountRetrieveParams),
            ),
            cast_to=MountRetrieveResponse,
        )

    async def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_mount_type: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_quality: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_mount_type: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_quality: Optional[List[str]] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MountListResponse:
        """
        Get Mounts

        Args:
          exclude_ids: Id should not be one of

          exclude_mount_type: Mount type should exclude one of

          exclude_quality: Quality should exclude one of

          include_ids: Id should be one of

          include_mount_type: Mount type should include one of

          include_quality: Quality should include one of

          lang: Language code

          limit: Items per page

          name: Name should be part of

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/mounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "exclude_mount_type": exclude_mount_type,
                        "exclude_quality": exclude_quality,
                        "include_ids": include_ids,
                        "include_mount_type": include_mount_type,
                        "include_quality": include_quality,
                        "lang": lang,
                        "limit": limit,
                        "name": name,
                        "page": page,
                    },
                    mount_list_params.MountListParams,
                ),
            ),
            cast_to=MountListResponse,
        )


class MountsResourceWithRawResponse:
    def __init__(self, mounts: MountsResource) -> None:
        self._mounts = mounts

        self.retrieve = to_raw_response_wrapper(
            mounts.retrieve,
        )
        self.list = to_raw_response_wrapper(
            mounts.list,
        )


class AsyncMountsResourceWithRawResponse:
    def __init__(self, mounts: AsyncMountsResource) -> None:
        self._mounts = mounts

        self.retrieve = async_to_raw_response_wrapper(
            mounts.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            mounts.list,
        )


class MountsResourceWithStreamingResponse:
    def __init__(self, mounts: MountsResource) -> None:
        self._mounts = mounts

        self.retrieve = to_streamed_response_wrapper(
            mounts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            mounts.list,
        )


class AsyncMountsResourceWithStreamingResponse:
    def __init__(self, mounts: AsyncMountsResource) -> None:
        self._mounts = mounts

        self.retrieve = async_to_streamed_response_wrapper(
            mounts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            mounts.list,
        )
