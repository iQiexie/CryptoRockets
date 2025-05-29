from fastapi import APIRouter, FastAPI

from app.api.routes import docs, game, task, telegram, user, user_task, shop


def setup_routes(app: FastAPI) -> FastAPI:
    router = APIRouter(prefix="/api/v1")

    router.include_router(router=telegram.router)
    router.include_router(router=docs.router)
    router.include_router(router=task.router)
    router.include_router(router=user.router)
    router.include_router(router=game.router)
    router.include_router(router=user_task.router)
    router.include_router(router=shop.router)

    app.include_router(router=router)

    return app
