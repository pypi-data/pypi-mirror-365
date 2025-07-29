# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillion_sdk import NextbillionSDK, AsyncNextbillionSDK
from nextbillion_sdk.types.skynet import SimpleResp

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAsset:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_bind(self, client: NextbillionSDK) -> None:
        asset = client.skynet.skynet.asset.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_bind(self, client: NextbillionSDK) -> None:
        response = client.skynet.skynet.asset.with_raw_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_bind(self, client: NextbillionSDK) -> None:
        with client.skynet.skynet.asset.with_streaming_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_bind(self, client: NextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.skynet.skynet.asset.with_raw_response.bind(
                id="",
                key="key=API_KEY",
                device_id="device_id",
            )


class TestAsyncAsset:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_bind(self, async_client: AsyncNextbillionSDK) -> None:
        asset = await async_client.skynet.skynet.asset.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_bind(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.skynet.asset.with_raw_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(SimpleResp, asset, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_bind(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.skynet.asset.with_streaming_response.bind(
            id="id",
            key="key=API_KEY",
            device_id="device_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(SimpleResp, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_bind(self, async_client: AsyncNextbillionSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.skynet.skynet.asset.with_raw_response.bind(
                id="",
                key="key=API_KEY",
                device_id="device_id",
            )
