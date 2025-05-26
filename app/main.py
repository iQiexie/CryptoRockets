import uvicorn
from fastapi import FastAPI

from app.adapters.base import Adapters
from app.api.dependencies.base import setup_dependencies
from app.config.config import get_config
from app.init.db import get_session_factory
from app.init.exceptions import setup_exceptions
from app.init.logs import setup_logs
from app.init.middlewares import setup_middlewares
from app.init.openapi import setup_openapi
from app.init.routes import setup_routes


def get_app() -> FastAPI:
    config = get_config()
    setup_logs(config=config.logs)

    session_factory, engine = get_session_factory(config=config.postgres)
    adapters = Adapters(config=config)

    fastapi = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=adapters.bot.setup)

    fastapi = setup_routes(app=fastapi)
    fastapi = setup_dependencies(
        app=fastapi,
        session_factory=session_factory,
        adapters=adapters,
        engine=engine,
    )
    fastapi = setup_exceptions(app=fastapi)
    fastapi = setup_openapi(app=fastapi)
    fastapi = setup_middlewares(app=fastapi, config=config, engine=engine, adapters=adapters)

    return fastapi


if __name__ == "__main__":
    uvicorn.run(
        "app.main:get_app",
        reload=False,
        port=8080,
        factory=True,
    )
