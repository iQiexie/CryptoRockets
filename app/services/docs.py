from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

from app.api.dependencies.stubs import dependency_app


class DocsService:
    def __init__(self, app: Annotated[FastAPI, Depends(dependency_app)]):
        self.app = app

    def get_docs(self) -> HTMLResponse:
        swagger_ui_parameters = self.app.swagger_ui_parameters or {} | {
            "persistAuthorization": True,
            "tryItOutEnabled": True,
            "displayRequestDuration": True,
            "defaultModelsExpandDepth": -1,
        }

        return get_swagger_ui_html(
            openapi_url=self.app.openapi_url,
            title=self.app.title,
            oauth2_redirect_url=self.app.swagger_ui_oauth2_redirect_url,
            swagger_ui_parameters=swagger_ui_parameters,
        )

    def get_openapi_json(self) -> dict[str, Any]:
        return self.app.openapi()
