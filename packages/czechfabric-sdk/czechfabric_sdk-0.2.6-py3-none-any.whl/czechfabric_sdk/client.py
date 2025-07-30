import asyncio
import json
from typing import Optional, List
from functools import wraps

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
from fastmcp.exceptions import ToolError
from functools import cache

import httpx
from fastmcp.utilities.inspect import ToolInfo
from mcp import Tool

from czechfabric_sdk.exceptions import (
    NetworkError,
    InvalidAPIKeyError,
    RateLimitExceededError,
    ToolExecutionError
)
from czechfabric_sdk.logging_config import logger
from czechfabric_sdk.models import (
    TripRequest,
    DeparturesRequest,
    GeocodeRequest,
    CoordinatesRequest,
    NearbyStopsRequest,
    StopMetadataRequest,
    ListStopsRequest
)


def retry(max_attempts=3, backoff_factor=0.5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = backoff_factor
            attempt = 1
            while True:
                try:
                    return await func(*args, **kwargs)
                except (httpx.HTTPError, ToolError) as e:
                    if attempt >= max_attempts:
                        logger.error(f"Exceeded max retries ({max_attempts}).")
                        raise NetworkError(f"Operation failed after {max_attempts} attempts.") from e
                    logger.warning(f"Attempt {attempt} failed ({e}); retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= 2
                    attempt += 1

        return wrapper

    return decorator


class CzechFabricClient:
    """
    Async client for CzechFabric MCP tools.
    """

    def __init__(self, api_key: str, base_url: str, timeout: float = 30.0) -> None:
        if not api_key:
            raise ValueError("API key required.")
        if not base_url:
            raise ValueError("Base URL required.")

        self._transport = StreamableHttpTransport(
            url=base_url,
            auth=BearerAuth(api_key),
        )
        self._client = Client(self._transport, timeout=timeout)

    @retry(max_attempts=3, backoff_factor=0.75)
    async def _call_tool(self, name: str, params: dict, cache: bool = False) -> str:
        if cache:
            from czechfabric_sdk.cache import cache_tool_call
            return await cache_tool_call(name, tuple(sorted(params.items())))

        async with self._client:
            try:
                logger.info(f"Calling tool '{name}' with {params}")
                result = await self._client.call_tool(name, params)
                logger.debug(f"Tool '{name}' response: {result.data}")
                return str(result.data)
            except ToolError as e:
                msg = str(e).lower()
                if "unauthorized" in msg or "forbidden" in msg:
                    raise InvalidAPIKeyError("Invalid API key.") from e
                if "rate limit" in msg or "too many requests" in msg:
                    raise RateLimitExceededError("Rate limit exceeded.") from e
                raise ToolExecutionError(f"Tool '{name}' failed: {e}") from e

    async def plan_trip(self, from_place: str, to_place: str, departure_time: Optional[str] = None) -> str:
        request = TripRequest(from_place=from_place, to_place=to_place, departure_time=departure_time)
        return await self._call_tool("plan_trip_between", request.model_dump())

    async def get_departures(self, stop_name: str, when: Optional[str] = None, arrive_by: Optional[str] = None,
                             mode: Optional[str] = None) -> str:
        request = DeparturesRequest(stop_name=stop_name, when=when, arrive_by=arrive_by, mode=mode)
        return await self._call_tool("get_departures", request.model_dump())

    async def geocode(self, name: str, use_cache: bool = True) -> str:
        request = GeocodeRequest(name=name)
        return await self._call_tool("geocode", request.model_dump(), cache=use_cache)

    async def departures_by_coordinates(self, latitude: float, longitude: float) -> str:
        request = CoordinatesRequest(latitude=latitude, longitude=longitude)
        return await self._call_tool("departures_by_coordinates", request.model_dump())

    async def reverse_geocode(self, latitude: float, longitude: float) -> str:
        request = CoordinatesRequest(latitude=latitude, longitude=longitude)
        return await self._call_tool("reverse_geocode", request.model_dump())

    async def find_all_stops_near(self, latitude: float, longitude: float, radius: int = 500) -> str:
        request = NearbyStopsRequest(latitude=latitude, longitude=longitude, radius=radius)
        return await self._call_tool("find_all_stops_near", request.model_dump())

    async def get_stop_metadata(self, stop_id: Optional[str] = None, stop_name: Optional[str] = None) -> str:
        request = StopMetadataRequest(stop_id=stop_id, stop_name=stop_name)
        return await self._call_tool("get_stop_metadata", request.model_dump())

    async def list_all_stops(self, name_contains: Optional[str] = None, zone: Optional[str] = None) -> str:
        request = ListStopsRequest(name_contains=name_contains, zone=zone)
        return await self._call_tool("list_all_stops", request.model_dump())

    @retry(max_attempts=3, backoff_factor=0.75)
    async def list_tools(self) -> list[Tool]:
        async with self._client:
            try:
                tools = await self._client.list_tools()
                logger.info(f"Fetched {len(tools)} tools.")
                return tools
            except Exception as e:
                logger.error(f"Tool listing failed: {e}")
                raise NetworkError("Failed to fetch list of tools.") from e

    async def get_tool_names(self) -> list[str]:
        tools = await self.list_tools()
        return [tool.name for tool in tools]

    async def get_tool_prompt_summary(self) -> str:
        tools = await self.list_tools()
        if not tools:
            return "No tools available."

        summary = "🧰 Available Tools:\n"
        for tool in tools:
            description = tool.description or "No description available."
            summary += f"\u2022 **{tool.name}**: {description}\n"
        return summary
