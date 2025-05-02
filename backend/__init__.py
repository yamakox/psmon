from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .job.metrics import collect_system_metrics
from . import api
from .db import database
from .config import settings

scheduler: BackgroundScheduler = None

# MARK: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # app開始時の初期化処理
    global scheduler
    database.init()
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect_system_metrics, trigger=IntervalTrigger(seconds=1))
    scheduler.start()

    # app実行中
    yield

    # app終了時の終了処理
    scheduler.shutdown()
    database.exit()

# MARK: create an app
def create_app():
    # Create an application instance
    app = FastAPI(lifespan=lifespan)

    # Initialize application instance
    app.include_router(api.v1.router)
    app.mount(
        path='/', 
        app=StaticFiles(directory='public', html=True), 
        name='public',
    )
    return app

