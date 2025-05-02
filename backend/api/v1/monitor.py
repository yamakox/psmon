from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...config import settings
from ...db import database
import time

# MARK: /api/v1/monitor
router = APIRouter(prefix='/monitor')

# MARK: MonitorRecord
class MonitorRecord(BaseModel):
    cpu_percent: float
    mem_percent: float

# MARK: MonitorResponse
class MonitorResponse(BaseModel):
    timestamp: int
    records: list[MonitorRecord] = []

# MARK: /api/v1/monitor
@router.get('')
def get_monitor_records():
    '''モニタリングしていたデータを取得する。'''
    if not database.client:
        raise HTTPException(status_code=500, detail='database client is not initialized.')
    return database.get_records()
