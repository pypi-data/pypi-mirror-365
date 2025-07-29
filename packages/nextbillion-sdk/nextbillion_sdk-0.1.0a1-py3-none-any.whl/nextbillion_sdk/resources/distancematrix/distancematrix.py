# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .json import (
    JsonResource,
    AsyncJsonResource,
    JsonResourceWithRawResponse,
    AsyncJsonResourceWithRawResponse,
    JsonResourceWithStreamingResponse,
    AsyncJsonResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["DistancematrixResource", "AsyncDistancematrixResource"]


class DistancematrixResource(SyncAPIResource):
    @cached_property
    def json(self) -> JsonResource:
        return JsonResource(self._client)

    @cached_property
    def with_raw_response(self) -> DistancematrixResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DistancematrixResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DistancematrixResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return DistancematrixResourceWithStreamingResponse(self)


class AsyncDistancematrixResource(AsyncAPIResource):
    @cached_property
    def json(self) -> AsyncJsonResource:
        return AsyncJsonResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDistancematrixResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDistancematrixResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDistancematrixResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncDistancematrixResourceWithStreamingResponse(self)


class DistancematrixResourceWithRawResponse:
    def __init__(self, distancematrix: DistancematrixResource) -> None:
        self._distancematrix = distancematrix

    @cached_property
    def json(self) -> JsonResourceWithRawResponse:
        return JsonResourceWithRawResponse(self._distancematrix.json)


class AsyncDistancematrixResourceWithRawResponse:
    def __init__(self, distancematrix: AsyncDistancematrixResource) -> None:
        self._distancematrix = distancematrix

    @cached_property
    def json(self) -> AsyncJsonResourceWithRawResponse:
        return AsyncJsonResourceWithRawResponse(self._distancematrix.json)


class DistancematrixResourceWithStreamingResponse:
    def __init__(self, distancematrix: DistancematrixResource) -> None:
        self._distancematrix = distancematrix

    @cached_property
    def json(self) -> JsonResourceWithStreamingResponse:
        return JsonResourceWithStreamingResponse(self._distancematrix.json)


class AsyncDistancematrixResourceWithStreamingResponse:
    def __init__(self, distancematrix: AsyncDistancematrixResource) -> None:
        self._distancematrix = distancematrix

    @cached_property
    def json(self) -> AsyncJsonResourceWithStreamingResponse:
        return AsyncJsonResourceWithStreamingResponse(self._distancematrix.json)
