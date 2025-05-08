from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from collections import defaultdict
from ...config import settings
from ...db import database
from datetime import datetime
from dateutil import tz
from ...job import metrics

# MARK: /api/v1/monitor
router = APIRouter(prefix='/monitor')

# MARK: MonitorRecord
class MonitorRecord(BaseModel):
    # time: datetime = Field(..., alias='_time')
    time_delta: float
    cpu_percent: float|None = None
    mem_available: float|None = None

# MARK: MonitorResponse
class MonitorResponse(BaseModel):
    timestamp: datetime
    mem_total: float
    records: list[MonitorRecord] = []

# MARK: MonitorResponseCompact
class MonitorResponseCompact(BaseModel):
    timestamp: datetime
    mem_total: float
    records: dict[str, list[datetime|float|None]]

# MARK: /api/v1/monitor/json
@router.get('/json', response_model=MonitorResponse)
def get_monitor_records_in_json():
    '''モニタリングしていたデータをJSON形式で取得する。'''
    if not database.client:
        raise HTTPException(status_code=500, detail='database client is not initialized.')
    timestamp, records = database.get_records_by_time()
    return MonitorResponse(
        timestamp=timestamp, 
        mem_total=metrics.get_mem_total(), 
        records=records, 
    )

# MARK: /api/v1/monitor
@router.get('', response_model=MonitorResponseCompact)
def get_monitor_records_by_field():
    '''モニタリングしていたデータをフィールドごとに取得する。'''
    if not database.client:
        raise HTTPException(status_code=500, detail='database client is not initialized.')
    timestamp, _records = database.get_records_by_time()
    _res = MonitorResponse(
        timestamp=timestamp, 
        mem_total=metrics.get_mem_total(), 
        records=_records, 
    )

    records = defaultdict(list)
    for record in _res.records:
        for key in MonitorRecord.model_fields.keys():
            records[key].append(getattr(record, key))
    return MonitorResponseCompact(
        timestamp=timestamp, 
        mem_total=metrics.get_mem_total(), 
        records=records, 
    )
