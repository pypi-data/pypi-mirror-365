# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from nextbillion_sdk import NextbillionSDK, AsyncNextbillionSDK
from nextbillion_sdk.types.skynet import (
    SimpleResp,
    ConfigListResponse,
    ConfigTestwebhookResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConfig:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: NextbillionSDK) -> None:
        config = client.skynet.config.create(
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: NextbillionSDK) -> None:
        config = client.skynet.config.create(
            key="key=API_KEY",
            cluster="america",
            webhook=["string"],
        )
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: NextbillionSDK) -> None:
        response = client.skynet.config.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: NextbillionSDK) -> None:
        with client.skynet.config.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(SimpleResp, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: NextbillionSDK) -> None:
        config = client.skynet.config.list(
            key="key=API_KEY",
        )
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: NextbillionSDK) -> None:
        config = client.skynet.config.list(
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: NextbillionSDK) -> None:
        response = client.skynet.config.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: NextbillionSDK) -> None:
        with client.skynet.config.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(ConfigListResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_testwebhook(self, client: NextbillionSDK) -> None:
        config = client.skynet.config.testwebhook(
            key="key=API_KEY",
        )
        assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_testwebhook(self, client: NextbillionSDK) -> None:
        response = client.skynet.config.with_raw_response.testwebhook(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_testwebhook(self, client: NextbillionSDK) -> None:
        with client.skynet.config.with_streaming_response.testwebhook(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConfig:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncNextbillionSDK) -> None:
        config = await async_client.skynet.config.create(
            key="key=API_KEY",
        )
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        config = await async_client.skynet.config.create(
            key="key=API_KEY",
            cluster="america",
            webhook=["string"],
        )
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.config.with_raw_response.create(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(SimpleResp, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.config.with_streaming_response.create(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(SimpleResp, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncNextbillionSDK) -> None:
        config = await async_client.skynet.config.list(
            key="key=API_KEY",
        )
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNextbillionSDK) -> None:
        config = await async_client.skynet.config.list(
            key="key=API_KEY",
            cluster="america",
        )
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.config.with_raw_response.list(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(ConfigListResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.config.with_streaming_response.list(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(ConfigListResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_testwebhook(self, async_client: AsyncNextbillionSDK) -> None:
        config = await async_client.skynet.config.testwebhook(
            key="key=API_KEY",
        )
        assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_testwebhook(self, async_client: AsyncNextbillionSDK) -> None:
        response = await async_client.skynet.config.with_raw_response.testwebhook(
            key="key=API_KEY",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_testwebhook(self, async_client: AsyncNextbillionSDK) -> None:
        async with async_client.skynet.config.with_streaming_response.testwebhook(
            key="key=API_KEY",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(ConfigTestwebhookResponse, config, path=["response"])

        assert cast(Any, response.is_closed) is True
