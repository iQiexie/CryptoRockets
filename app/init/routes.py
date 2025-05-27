from fastapi import APIRouter, FastAPI

from app.api.routes import docs, task, telegram, user, game


def setup_routes(app: FastAPI) -> FastAPI:
    router = APIRouter(prefix="/api/v1")

    router.include_router(router=telegram.router)
    router.include_router(router=docs.router)
    router.include_router(router=task.router)
    router.include_router(router=user.router)
    router.include_router(router=game.router)

    app.include_router(router=router)

    return app
