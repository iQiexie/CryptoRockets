from datetime import datetime
from types import SimpleNamespace
from typing import Any

import aiohttp
from aiohttp import (
    ClientConnectionError,
    ClientResponse,
    ClientSession,
    TraceRequestChunkSentParams,
    TraceRequestEndParams,
    TraceRequestExceptionParams,
    TraceRequestStartParams,
    hdrs,
)
from pydantic_core import from_json, to_json

from app.config.constants import (
    DEFAULT_HTTP_TIMEOUT,
    LOGGING_SENSITIVE_FIELDS,
    LOGGING_SENSITIVE_REPLACEMENT,
)
from app.utils import struct_log


async def on_request_start(_: ClientSession, context: SimpleNamespace, params: TraceRequestStartParams) -> None:
    context.method = params.method
    context.url = params.url.human_repr()


async def on_request_end(_: ClientSession, context: SimpleNamespace, params: TraceRequestEndParams) -> None:
    ctype = params.response.headers.get(hdrs.CONTENT_TYPE, "").lower()

    if ctype == "application/json":
        response = await params.response.json()
    else:
        response = await params.response.text()

    if context.trace_request_ctx["log"]:
        struct_log(
            event="Request sent" if params.response.ok else "Request sent, got an error",
            request_duration=(datetime.utcnow() - context.trace_request_ctx["start_time"]).total_seconds(),
            request=dict(
                headers=context.headers,
                body=getattr(context, "body", ""),
                method=context.method,
                url=context.url,
            ),
            response=dict(
                body=response,
            ),
        )

    if context.trace_request_ctx["raise"]:
        params.response.raise_for_status()


async def on_request_chunk_sent(
    _: ClientSession,
    context: SimpleNamespace,
    chunk: TraceRequestChunkSentParams,
) -> None:
    try:
        context.body = from_json(chunk.chunk)
    except ValueError:
        context.body = chunk.chunk.decode("utf-8")


async def on_request_exception(
    _: ClientSession,
    context: SimpleNamespace,
    detail: TraceRequestExceptionParams,
) -> None:
    if not isinstance(detail.exception, ClientConnectionError):
        raise detail.exception

    if context.trace_request_ctx["log"]:
        struct_log(
            event="Sending request",
            method=context.method,
            url=context.url,
            headers=context.headers,
            body=context.trace_request_ctx.get("json") or context.trace_request_ctx.get("data"),
        )

    raise detail.exception


class AioHttpClient:
    auth_header: dict[str, str]
    base_url: str

    def __init__(self, auth_header: dict[str, str], base_url: str):
        self.auth_header = auth_header
        self.base_url = base_url

    @staticmethod
    def _get_session() -> aiohttp.ClientSession:
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
        trace_config.on_request_end.append(on_request_end)
        trace_config.on_request_exception.append(on_request_exception)

        return aiohttp.ClientSession(
            json_serialize=lambda x: to_json(x).decode(),
            trace_configs=[trace_config],
        )

    async def request(
        self,
        method: str,
        url: str,
        return_json: bool = True,
        full_url: bool = False,
        raise_exceptions: bool = True,
        log: bool = True,
        headers: dict[str, str] = None,
        timeout: int | None = DEFAULT_HTTP_TIMEOUT,
        params: dict[str, Any] = None,
        json: dict[str, Any] = None,
        data: dict[str, Any] = None,
    ) -> dict | ClientResponse:
        headers = headers or {}
        headers |= self.auth_header

        if not full_url:
            url = self.base_url + url

        async with self._get_session() as client:
            response = await client.request(
                method=method,
                url=url,
                timeout=timeout,
                headers=headers,
                params=params,
                json=json,
                data=data,
                raise_for_status=False,
                ssl=False,
                trace_request_ctx={
                    "json": json,
                    "data": data,
                    "raise": raise_exceptions,
                    "start_time": datetime.utcnow(),
                    "log": log,
                },
            )

            if return_json:
                return await response.json()

            return response
