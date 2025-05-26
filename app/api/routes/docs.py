from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette.responses import HTMLResponse

from app.api.dependencies.auth import auth_basic
from app.services.docs import DocsService

router = APIRouter(tags=["Docs"])


@router.get(
    path="/docs",
    include_in_schema=False,
)
async def get_docs(
    _: Annotated[None, Depends(auth_basic)],
    docs_service: Annotated[DocsService, Depends()],
) -> HTMLResponse:
    return docs_service.get_docs()


@router.get(
    path="/openapi.json",
    include_in_schema=False,
)
async def get_openapi_json(
    _: Annotated[None, Depends(auth_basic)],
    docs_service: Annotated[DocsService, Depends()],
) -> dict[str, Any]:
    return docs_service.get_openapi_json()
