from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from importlib.metadata import version

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
        try:
            return VersionResponse(version=version('psmon'))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
