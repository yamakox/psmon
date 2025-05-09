from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path, PurePosixPath
import logging

'''
    # StaticFilesを使ってローカルファイルを公開できるが、
    # アセット以外のURLパスはVue routerを実装したindex.htmlを返す必要がある。
    public_path = base_path / 'public'
    app.mount(
        path='/', 
        app=StaticFiles(directory=str(public_path), html=True), 
        name='public',
    )
'''

public_path: Path|None = None
index_path: Path|None = None

# MARK: /
def create_router(base_path: Path) -> APIRouter:
    router = APIRouter(prefix='', tags=['frontend'])  # prefixは'/'で終わってはいけない

    global public_path, index_path
    if not public_path:
        public_path = (base_path / 'public').resolve()
        if not public_path.is_dir():
            raise Exception('public/ does NOT exist.')
    if not index_path:
        index_path = (public_path / 'index.html').resolve()
        if not index_path.is_file():
            raise Exception('public/index.html does NOT exist.')


    # MARK: /.well-known/*
    @router.get('/.well-known/{path:path}')
    def handle_unknown_well_known(path: str):
        raise HTTPException(status_code=404, detail="Not implemented")

    # MARK: /*
    @router.get('/{path:path}')
    def get_frontend(path: str):
        logging.debug(f'get_frontend {path=}')

        # ローカルファイルの取得
        local_path = (public_path / Path(PurePosixPath(path))).resolve()
        if not local_path.is_relative_to(base_path):
            raise HTTPException(status_code=403, detail="Access denied")
        logging.debug(f'get_frontend {local_path=}')
        if local_path.is_file():
            return FileResponse(local_path)

        # index.htmlの取得
        return FileResponse(index_path)

    return router
