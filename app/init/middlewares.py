import os

import structlog
from fastapi import FastAPI
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.adapters.base import Adapters
from app.api.middlewares.logs import LoggingMiddleware
from app.config.config import Config, PrometheusConfig
from app.init.oltp import setup_oltp

logger = structlog.stdlib.get_logger()


def setup_prometheus(app: FastAPI, config: PrometheusConfig) -> FastAPI:
    app.add_middleware(
        PrometheusMiddleware,
        app_name=config.PROMETHEUS_APP_NAME,
        prefix=config.PROMETHEUS_PREFIX,
        buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0],
        skip_paths=["/metrics"],
        skip_methods=["OPTIONS"],
        group_paths=True,
        labels={
            "hostname": os.getenv("HOSTNAME", "back_service"),
        },
    )

    app.add_route("/metrics", handle_metrics)
    return app


def setup_middlewares(app: FastAPI, config: Config, engine: AsyncEngine, adapters: Adapters) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

    if config.logs.LOGS_IS_ENABLED:
        app.add_middleware(LoggingMiddleware, adapters=adapters)

    if config.logs.LOGS_OTLP_ENDPOINT and config.logs.LOGS_OLTP_ENABLED:
        setup_oltp(
            protocol="http",
            endpoint=config.logs.LOGS_OTLP_ENDPOINT,
            attributes={"service.name": "backend"},
            headers={"Authorization": config.logs.LOGS_OTLP_TOKEN},
        )

        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        FastAPIInstrumentor.instrument_app(app=app, excluded_urls="/metrics")
        AioHttpClientInstrumentor().instrument()
        SystemMetricsInstrumentor().instrument(base="full")

    return app
