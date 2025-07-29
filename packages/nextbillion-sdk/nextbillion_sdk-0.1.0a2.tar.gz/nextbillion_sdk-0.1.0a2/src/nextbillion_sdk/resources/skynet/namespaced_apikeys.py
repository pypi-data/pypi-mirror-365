# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.skynet import (
    namespaced_apikey_namespaced_apikeys_params,
    namespaced_apikey_delete_namespaced_apikeys_params,
)
from ...types.skynet.namespaced_apikey_namespaced_apikeys_response import NamespacedApikeyNamespacedApikeysResponse
from ...types.skynet.namespaced_apikey_delete_namespaced_apikeys_response import (
    NamespacedApikeyDeleteNamespacedApikeysResponse,
)

__all__ = ["NamespacedApikeysResource", "AsyncNamespacedApikeysResource"]


class NamespacedApikeysResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NamespacedApikeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return NamespacedApikeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NamespacedApikeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return NamespacedApikeysResourceWithStreamingResponse(self)

    def delete_namespaced_apikeys(
        self,
        *,
        key: str,
        key_to_delete: str,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NamespacedApikeyDeleteNamespacedApikeysResponse:
        """
        Delete namespace under a parent key

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API. Please note for the delete namespace key operation another namespace key
              cannot be used.

              The namespace created using this key can be managed using the APIs & Services >
              Credentials section of user’s
              [NextBillion Console](https://console.nextbillion.ai).

          key_to_delete: Specify the key to be deleted.

          namespace: Specify the name of the `namespace` to which the \\``key_to_delete\\`` belongs.
              Please note that a namespace key cannot be deleted using another namespace key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/skynet/namespaced-apikeys",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "key_to_delete": key_to_delete,
                        "namespace": namespace,
                    },
                    namespaced_apikey_delete_namespaced_apikeys_params.NamespacedApikeyDeleteNamespacedApikeysParams,
                ),
            ),
            cast_to=NamespacedApikeyDeleteNamespacedApikeysResponse,
        )

    def namespaced_apikeys(
        self,
        *,
        key: str,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NamespacedApikeyNamespacedApikeysResponse:
        """
        Create namespace under a parent key

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          namespace: Specify a name for the `namespace`. If the namespace specified is unique then a
              new namespace along with a new key is created. Whereas if the specified
              `namespace` is not unique, a new key will be created in the existing
              `namespace`. Please note that a `namespace` cannot be created using another
              namespace key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/skynet/namespaced-apikeys",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "key": key,
                        "namespace": namespace,
                    },
                    namespaced_apikey_namespaced_apikeys_params.NamespacedApikeyNamespacedApikeysParams,
                ),
            ),
            cast_to=NamespacedApikeyNamespacedApikeysResponse,
        )


class AsyncNamespacedApikeysResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNamespacedApikeysResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNamespacedApikeysResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNamespacedApikeysResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/nextbillion-ai/nextbillion-sdk-python#with_streaming_response
        """
        return AsyncNamespacedApikeysResourceWithStreamingResponse(self)

    async def delete_namespaced_apikeys(
        self,
        *,
        key: str,
        key_to_delete: str,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NamespacedApikeyDeleteNamespacedApikeysResponse:
        """
        Delete namespace under a parent key

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API. Please note for the delete namespace key operation another namespace key
              cannot be used.

              The namespace created using this key can be managed using the APIs & Services >
              Credentials section of user’s
              [NextBillion Console](https://console.nextbillion.ai).

          key_to_delete: Specify the key to be deleted.

          namespace: Specify the name of the `namespace` to which the \\``key_to_delete\\`` belongs.
              Please note that a namespace key cannot be deleted using another namespace key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/skynet/namespaced-apikeys",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "key_to_delete": key_to_delete,
                        "namespace": namespace,
                    },
                    namespaced_apikey_delete_namespaced_apikeys_params.NamespacedApikeyDeleteNamespacedApikeysParams,
                ),
            ),
            cast_to=NamespacedApikeyDeleteNamespacedApikeysResponse,
        )

    async def namespaced_apikeys(
        self,
        *,
        key: str,
        namespace: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NamespacedApikeyNamespacedApikeysResponse:
        """
        Create namespace under a parent key

        Args:
          key: A key is a unique identifier that is required to authenticate a request to the
              API.

          namespace: Specify a name for the `namespace`. If the namespace specified is unique then a
              new namespace along with a new key is created. Whereas if the specified
              `namespace` is not unique, a new key will be created in the existing
              `namespace`. Please note that a `namespace` cannot be created using another
              namespace key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/skynet/namespaced-apikeys",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "key": key,
                        "namespace": namespace,
                    },
                    namespaced_apikey_namespaced_apikeys_params.NamespacedApikeyNamespacedApikeysParams,
                ),
            ),
            cast_to=NamespacedApikeyNamespacedApikeysResponse,
        )


class NamespacedApikeysResourceWithRawResponse:
    def __init__(self, namespaced_apikeys: NamespacedApikeysResource) -> None:
        self._namespaced_apikeys = namespaced_apikeys

        self.delete_namespaced_apikeys = to_raw_response_wrapper(
            namespaced_apikeys.delete_namespaced_apikeys,
        )
        self.namespaced_apikeys = to_raw_response_wrapper(
            namespaced_apikeys.namespaced_apikeys,
        )


class AsyncNamespacedApikeysResourceWithRawResponse:
    def __init__(self, namespaced_apikeys: AsyncNamespacedApikeysResource) -> None:
        self._namespaced_apikeys = namespaced_apikeys

        self.delete_namespaced_apikeys = async_to_raw_response_wrapper(
            namespaced_apikeys.delete_namespaced_apikeys,
        )
        self.namespaced_apikeys = async_to_raw_response_wrapper(
            namespaced_apikeys.namespaced_apikeys,
        )


class NamespacedApikeysResourceWithStreamingResponse:
    def __init__(self, namespaced_apikeys: NamespacedApikeysResource) -> None:
        self._namespaced_apikeys = namespaced_apikeys

        self.delete_namespaced_apikeys = to_streamed_response_wrapper(
            namespaced_apikeys.delete_namespaced_apikeys,
        )
        self.namespaced_apikeys = to_streamed_response_wrapper(
            namespaced_apikeys.namespaced_apikeys,
        )


class AsyncNamespacedApikeysResourceWithStreamingResponse:
    def __init__(self, namespaced_apikeys: AsyncNamespacedApikeysResource) -> None:
        self._namespaced_apikeys = namespaced_apikeys

        self.delete_namespaced_apikeys = async_to_streamed_response_wrapper(
            namespaced_apikeys.delete_namespaced_apikeys,
        )
        self.namespaced_apikeys = async_to_streamed_response_wrapper(
            namespaced_apikeys.namespaced_apikeys,
        )
