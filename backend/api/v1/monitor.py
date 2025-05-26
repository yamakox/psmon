from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from collections import defaultdict
from datetime import datetime
from dateutil import tz
from pathlib import Path
from ...db import database
from ...job import metrics
from ...common import settings

# MARK: MonitorRecord
class MonitorRecord(BaseModel):
    time: datetime = Field(..., alias='_time')
    #time_delta: float
    cpu_percent_max: float|None = None
    cpu_percent_mean: float|None = None
    mem_available_max: float|None = None
    mem_available_mean: float|None = None
    disk_used_max: float|None = None
    disk_used_mean: float|None = None

# MARK: MonitorResponse
class MonitorResponse(BaseModel):
    timestamp: datetime
    mem_total: float
    disk_total: float
    records: list[MonitorRecord] = []

# MARK: MonitorResponseCompact
class MonitorResponseCompact(BaseModel):
    timestamp: datetime
    mem_total: float
    disk_total: float
    records: dict[str, list[datetime|float|None]]

def create_router(base_path: Path) -> APIRouter:
    # MARK: /api/v1/monitor
    router = APIRouter(prefix='/monitor')

    # MARK: /api/v1/monitor/durations
    @router.get('/durations', response_model=list[settings.Duration])
    def get_durations():
        '''モニタリングの時間間隔のリストを取得する。'''
        return settings.DURATIONS

    # MARK: /api/v1/monitor/json
    @router.get('/json', response_model=MonitorResponse)
    def get_monitor_records_in_json(
        duration_index: int = Query(default=0, description='duration index to query'),
        start_time: datetime|None = Query(default=None, description='start time to query')
    ):
        '''モニタリングしていたデータをJSON形式で取得する。'''
        if not database.client:
            raise HTTPException(status_code=500, detail='database client is not initialized.')
        timestamp, records = database.get_system_stats_records_by_time(
            duration_index=duration_index,
            start_time=start_time,
        )
        return MonitorResponse(
            timestamp=timestamp, 
            mem_total=metrics.get_mem_total(), 
            disk_total=metrics.get_disk_total(), 
            records=records, 
        )

    # MARK: /api/v1/monitor
    @router.get('', response_model=MonitorResponseCompact)
    def get_monitor_records_by_field(
        duration_index: int = Query(default=0, description='duration index to query'),
        start_time: datetime|None = Query(default=None, description='start time to query')
    ):
        '''モニタリングしていたデータをフィールドごとに取得する。'''
        if not database.client:
            raise HTTPException(status_code=500, detail='database client is not initialized.')
        timestamp, _records = database.get_system_stats_records_by_time(
            duration_index=duration_index,
            start_time=start_time,
        )
        _res = MonitorResponse(
            timestamp=timestamp, 
            mem_total=metrics.get_mem_total(), 
            disk_total=metrics.get_disk_total(), 
            records=_records, 
        )

        records = defaultdict(list)
        for record in _res.records:
            for key in MonitorRecord.model_fields.keys():
                records[key].append(getattr(record, key))
        return MonitorResponseCompact(
            timestamp=timestamp, 
            mem_total=_res.mem_total, 
            disk_total=_res.disk_total, 
            records=records, 
        )

    return router
