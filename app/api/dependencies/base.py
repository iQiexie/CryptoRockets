from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker

from app.adapters.base import Adapters
from app.api.dependencies.stubs import (
    dependency_adapters,
    dependency_app,
    dependency_services,
    dependency_session_factory,
    dependency_websocket_service,
)
from app.services.base.services import Services
from app.services.websocket import WebsocketService


def setup_dependencies(
    app: FastAPI,
    session_factory: sessionmaker,
    adapters: Adapters,
    engine: AsyncEngine,
) -> FastAPI:
    services = Services(session_factory=session_factory, adapters=adapters, engine=engine)
    websocket_service = WebsocketService(session_factory=session_factory, adapters=adapters)

    app.dependency_overrides[dependency_adapters] = lambda: adapters
    app.dependency_overrides[dependency_session_factory] = lambda: session_factory
    app.dependency_overrides[dependency_app] = lambda: app
    app.dependency_overrides[dependency_services] = lambda: services
    app.dependency_overrides[dependency_websocket_service] = lambda: websocket_service

    return app
