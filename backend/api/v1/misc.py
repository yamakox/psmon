from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from backend import __version__

# MARK: VersionResponse
class VersionResponse(BaseModel):
    version: str

def create_router(base_path: Path) -> APIRouter:
    # MARK: /api/v1/misc
    router = APIRouter(prefix='/misc')

    # MARK: /api/v1/misc/version
    @router.get('/version', response_model=VersionResponse)
    def get_version():
        '''バージョン情報を取得する。'''
        return VersionResponse(version=__version__)

    return router

