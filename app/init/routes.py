from fastapi import APIRouter, FastAPI

from app.api.routes import callbacks, docs, game, shop, task, telegram, user, user_task, ads


def setup_routes(app: FastAPI) -> FastAPI:
    router = APIRouter(prefix="/api/v1")

    router.include_router(router=telegram.router)
    router.include_router(router=docs.router)
    router.include_router(router=task.router)
    router.include_router(router=user.router)
    router.include_router(router=game.router)
    router.include_router(router=user_task.router)
    router.include_router(router=shop.router)
    router.include_router(router=callbacks.router)
    router.include_router(router=ads.router)

    app.include_router(router=router)

    return app
