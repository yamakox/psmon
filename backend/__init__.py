__version__ = '0.0.0'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pathlib import Path
from .common import settings
from .db import database
from .job.metrics import collect_metrics
from . import api
from . import frontend

scheduler: BackgroundScheduler = None

# MARK: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # app開始時の初期化処理
    global scheduler
    database.init()
    collect_metrics(True)   # 初回のcpu_percentのキャッシュ用
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect_metrics, trigger=IntervalTrigger(seconds=settings.METRICS_INTERVAL))
    scheduler.start()

    # app実行中
    yield

    # app終了時の終了処理
    scheduler.shutdown()
    database.exit()

# MARK: create an app
def create_app(base_path: Path) -> FastAPI:
    # Create an application instance
    app = FastAPI(lifespan=lifespan)

    # CORS対策
    origins = [
        'http://localhost:5173', 
    #   'https://hogehoge.com', 
    ]
    app.add_middleware(
        CORSMiddleware, 
        allow_origins=origins, 
        allow_credentials=True, 
        allow_methods=['*'], 
        allow_headers=['*'], 
    )

    # Initialize application instance
    app.include_router(api.v1.create_router(base_path=base_path))
    app.include_router(frontend.create_router(base_path=base_path))

    return app

