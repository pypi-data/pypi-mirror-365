# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .asset import (
    AssetResource,
    AsyncAssetResource,
    AssetResourceWithRawResponse,
    AsyncAssetResourceWithRawResponse,
    AssetResourceWithStreamingResponse,
    AsyncAssetResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["SkynetResource", "AsyncSkynetResource"]


class SkynetResource(SyncAPIResource):
    @cached_property
    def asset(self) -> AssetResource:
        return AssetResource(self._client)

    @cached_property
    def with_raw_response(self) -> SkynetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SkynetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SkynetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return SkynetResourceWithStreamingResponse(self)


class AsyncSkynetResource(AsyncAPIResource):
    @cached_property
    def asset(self) -> AsyncAssetResource:
        return AsyncAssetResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSkynetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSkynetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSkynetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncSkynetResourceWithStreamingResponse(self)


class SkynetResourceWithRawResponse:
    def __init__(self, skynet: SkynetResource) -> None:
        self._skynet = skynet

    @cached_property
    def asset(self) -> AssetResourceWithRawResponse:
        return AssetResourceWithRawResponse(self._skynet.asset)


class AsyncSkynetResourceWithRawResponse:
    def __init__(self, skynet: AsyncSkynetResource) -> None:
        self._skynet = skynet

    @cached_property
    def asset(self) -> AsyncAssetResourceWithRawResponse:
        return AsyncAssetResourceWithRawResponse(self._skynet.asset)


class SkynetResourceWithStreamingResponse:
    def __init__(self, skynet: SkynetResource) -> None:
        self._skynet = skynet

    @cached_property
    def asset(self) -> AssetResourceWithStreamingResponse:
        return AssetResourceWithStreamingResponse(self._skynet.asset)


class AsyncSkynetResourceWithStreamingResponse:
    def __init__(self, skynet: AsyncSkynetResource) -> None:
        self._skynet = skynet

    @cached_property
    def asset(self) -> AsyncAssetResourceWithStreamingResponse:
        return AsyncAssetResourceWithStreamingResponse(self._skynet.asset)
