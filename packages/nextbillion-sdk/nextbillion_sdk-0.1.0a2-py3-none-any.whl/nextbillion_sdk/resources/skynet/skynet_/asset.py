# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.skynet.skynet_ import asset_bind_params
from ....types.skynet.simple_resp import SimpleResp

__all__ = ["AssetResource", "AsyncAssetResource"]


class AssetResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AssetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AssetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AssetResourceWithStreamingResponse(self)

    def bind(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Bind asset to device

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: Device ID to be linked to the `asset` identified by `id`.

              Please note that the device needs to be linked to an `asset` before using it in
              the _Upload locations of an Asset_ method for sending GPS information about the
              `asset`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/skynet/skynet/asset/{id}/bind",
            body=maybe_transform({"device_id": device_id}, asset_bind_params.AssetBindParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"key": key}, asset_bind_params.AssetBindParams),
            ),
            cast_to=SimpleResp,
        )


class AsyncAssetResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAssetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncAssetResourceWithStreamingResponse(self)

    async def bind(
        self,
        id: str,
        *,
        key: str,
        device_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SimpleResp:
        """
        Bind asset to device

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          device_id: Device ID to be linked to the `asset` identified by `id`.

              Please note that the device needs to be linked to an `asset` before using it in
              the _Upload locations of an Asset_ method for sending GPS information about the
              `asset`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/skynet/skynet/asset/{id}/bind",
            body=await async_maybe_transform({"device_id": device_id}, asset_bind_params.AssetBindParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"key": key}, asset_bind_params.AssetBindParams),
            ),
            cast_to=SimpleResp,
        )


class AssetResourceWithRawResponse:
    def __init__(self, asset: AssetResource) -> None:
        self._asset = asset

        self.bind = to_raw_response_wrapper(
            asset.bind,
        )


class AsyncAssetResourceWithRawResponse:
    def __init__(self, asset: AsyncAssetResource) -> None:
        self._asset = asset

        self.bind = async_to_raw_response_wrapper(
            asset.bind,
        )


class AssetResourceWithStreamingResponse:
    def __init__(self, asset: AssetResource) -> None:
        self._asset = asset

        self.bind = to_streamed_response_wrapper(
            asset.bind,
        )


class AsyncAssetResourceWithStreamingResponse:
    def __init__(self, asset: AsyncAssetResource) -> None:
        self._asset = asset

        self.bind = async_to_streamed_response_wrapper(
            asset.bind,
        )
