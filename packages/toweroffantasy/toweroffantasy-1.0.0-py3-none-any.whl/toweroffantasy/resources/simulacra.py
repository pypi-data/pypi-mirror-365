# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..types import LangsEnum, simulacra_list_params, simulacra_retrieve_params, simulacra_liked_gifts_params
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
from ..types.simulacra_list_response import SimulacraListResponse
from ..types.simulacra_retrieve_response import SimulacraRetrieveResponse
from ..types.simulacra_liked_gifts_response import SimulacraLikedGiftsResponse

__all__ = ["SimulacraResource", "AsyncSimulacraResource"]


class SimulacraResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SimulacraResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return SimulacraResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SimulacraResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return SimulacraResourceWithStreamingResponse(self)

    def retrieve(
        self,
        simulacrum_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraRetrieveResponse:
        """
        Get Simulacrum

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not simulacrum_id:
            raise ValueError(f"Expected a non-empty value for `simulacrum_id` but received {simulacrum_id!r}")
        return self._get(
            f"/simulacra/{simulacrum_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"lang": lang}, simulacra_retrieve_params.SimulacraRetrieveParams),
            ),
            cast_to=SimulacraRetrieveResponse,
        )

    def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_rarities: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_sex: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_rarities: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_sex: Optional[List[str]] | NotGiven = NOT_GIVEN,
        is_limited: Optional[bool] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        no_weapon: Optional[bool] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraListResponse:
        """
        Get Simulacra

        Args:
          exclude_ids: Id should not be one of

          exclude_rarities: Rarity should exclude one of

          exclude_sex: Sex should exclude one of

          include_ids: Id should be one of

          include_rarities: Rarity should include one of

          include_sex: Sex should include one of

          is_limited: Is limited weapon (Red Nucleous)

          lang: Language code

          limit: Items per page

          name: Name should be part of

          no_weapon: No weapon (Polymorph)

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/simulacra",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "exclude_rarities": exclude_rarities,
                        "exclude_sex": exclude_sex,
                        "include_ids": include_ids,
                        "include_rarities": include_rarities,
                        "include_sex": include_sex,
                        "is_limited": is_limited,
                        "lang": lang,
                        "limit": limit,
                        "name": name,
                        "no_weapon": no_weapon,
                        "page": page,
                    },
                    simulacra_list_params.SimulacraListParams,
                ),
            ),
            cast_to=SimulacraListResponse,
        )

    def liked_gifts(
        self,
        simulacrum_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraLikedGiftsResponse:
        """
        Get Simulacrum Liked Gifts

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not simulacrum_id:
            raise ValueError(f"Expected a non-empty value for `simulacrum_id` but received {simulacrum_id!r}")
        return self._get(
            f"/simulacra/{simulacrum_id}/gifts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"lang": lang}, simulacra_liked_gifts_params.SimulacraLikedGiftsParams),
            ),
            cast_to=SimulacraLikedGiftsResponse,
        )


class AsyncSimulacraResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSimulacraResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSimulacraResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSimulacraResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/biellSilva/toweroffantasy.sdk#with_streaming_response
        """
        return AsyncSimulacraResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        simulacrum_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraRetrieveResponse:
        """
        Get Simulacrum

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not simulacrum_id:
            raise ValueError(f"Expected a non-empty value for `simulacrum_id` but received {simulacrum_id!r}")
        return await self._get(
            f"/simulacra/{simulacrum_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"lang": lang}, simulacra_retrieve_params.SimulacraRetrieveParams),
            ),
            cast_to=SimulacraRetrieveResponse,
        )

    async def list(
        self,
        *,
        exclude_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_rarities: Optional[List[str]] | NotGiven = NOT_GIVEN,
        exclude_sex: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_ids: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_rarities: Optional[List[str]] | NotGiven = NOT_GIVEN,
        include_sex: Optional[List[str]] | NotGiven = NOT_GIVEN,
        is_limited: Optional[bool] | NotGiven = NOT_GIVEN,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        no_weapon: Optional[bool] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraListResponse:
        """
        Get Simulacra

        Args:
          exclude_ids: Id should not be one of

          exclude_rarities: Rarity should exclude one of

          exclude_sex: Sex should exclude one of

          include_ids: Id should be one of

          include_rarities: Rarity should include one of

          include_sex: Sex should include one of

          is_limited: Is limited weapon (Red Nucleous)

          lang: Language code

          limit: Items per page

          name: Name should be part of

          no_weapon: No weapon (Polymorph)

          page: Page number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/simulacra",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "exclude_ids": exclude_ids,
                        "exclude_rarities": exclude_rarities,
                        "exclude_sex": exclude_sex,
                        "include_ids": include_ids,
                        "include_rarities": include_rarities,
                        "include_sex": include_sex,
                        "is_limited": is_limited,
                        "lang": lang,
                        "limit": limit,
                        "name": name,
                        "no_weapon": no_weapon,
                        "page": page,
                    },
                    simulacra_list_params.SimulacraListParams,
                ),
            ),
            cast_to=SimulacraListResponse,
        )

    async def liked_gifts(
        self,
        simulacrum_id: str,
        *,
        lang: LangsEnum | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimulacraLikedGiftsResponse:
        """
        Get Simulacrum Liked Gifts

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not simulacrum_id:
            raise ValueError(f"Expected a non-empty value for `simulacrum_id` but received {simulacrum_id!r}")
        return await self._get(
            f"/simulacra/{simulacrum_id}/gifts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"lang": lang}, simulacra_liked_gifts_params.SimulacraLikedGiftsParams
                ),
            ),
            cast_to=SimulacraLikedGiftsResponse,
        )


class SimulacraResourceWithRawResponse:
    def __init__(self, simulacra: SimulacraResource) -> None:
        self._simulacra = simulacra

        self.retrieve = to_raw_response_wrapper(
            simulacra.retrieve,
        )
        self.list = to_raw_response_wrapper(
            simulacra.list,
        )
        self.liked_gifts = to_raw_response_wrapper(
            simulacra.liked_gifts,
        )


class AsyncSimulacraResourceWithRawResponse:
    def __init__(self, simulacra: AsyncSimulacraResource) -> None:
        self._simulacra = simulacra

        self.retrieve = async_to_raw_response_wrapper(
            simulacra.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            simulacra.list,
        )
        self.liked_gifts = async_to_raw_response_wrapper(
            simulacra.liked_gifts,
        )


class SimulacraResourceWithStreamingResponse:
    def __init__(self, simulacra: SimulacraResource) -> None:
        self._simulacra = simulacra

        self.retrieve = to_streamed_response_wrapper(
            simulacra.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            simulacra.list,
        )
        self.liked_gifts = to_streamed_response_wrapper(
            simulacra.liked_gifts,
        )


class AsyncSimulacraResourceWithStreamingResponse:
    def __init__(self, simulacra: AsyncSimulacraResource) -> None:
        self._simulacra = simulacra

        self.retrieve = async_to_streamed_response_wrapper(
            simulacra.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            simulacra.list,
        )
        self.liked_gifts = async_to_streamed_response_wrapper(
            simulacra.liked_gifts,
        )
