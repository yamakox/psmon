from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.flux_table import TableList
from ..common import settings
from datetime import datetime, timedelta
from dateutil import tz
from typing import Any

client: InfluxDBClient|None = None

# MARK: init & exit
def init():
    global client
    if client:
        return
    client = InfluxDBClient(
        url=settings.INFLUXDB_URL, 
        token=settings.INFLUXDB_TOKEN, 
        org=settings.INFLUXDB_ORG, 
    )

def exit():
    global client
    if client is None:
        return
    client.close()
    client = None

# MARK: write & get records
_MEASUREMENT_SYS_STATS = 'system_stats'
_MEASUREMENT_PROCESS_CPU = 'process_cpu'

def write_system_stats_record(time: int, **kwargs):
    '''psutilで取得したシステム状態をDBのレコードに保存する。'''
    if not client:
        raise Exception('No database client object.')
    point = dict(
        measurement=_MEASUREMENT_SYS_STATS, 
        fields=kwargs,
        time=time
    )
    (client
        .write_api(write_options=SYNCHRONOUS)
        .write(
            bucket=settings.INFLUXDB_BUCKET, 
            record=point, 
        )
    )

def write_process_cpu_record(time: int, processes: list[tuple[float, int, str]]):
    '''psutilで取得したCPU使用率が高いプロセスのリストをDBのレコードに保存する。'''
    if not client:
        raise Exception('No database client object.')
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for cpu, pid, name in processes:
        point = (
            Point(_MEASUREMENT_PROCESS_CPU)
            .time(time)
            .field('cpu_percent', cpu)
            .field('pid', pid)
            .field('name', name)
        )
        write_api.write(
            bucket=settings.INFLUXDB_BUCKET, 
            record=point, 
        )

def get_system_stats_records_by_time(every: str = "1m", start_time: datetime|None = None):
    '''DBに保存してあったpsutilのデータを時間ごとに取得する。
    
    Args:
        every (str): 時間ごとの間隔
        start_time (datetime|None): 取得する時間の開始時刻、Noneの場合は6時間前(now() - 6h)から取得する

    Returns:
        tuple[datetime, list[dict]]: 取得したデータの時刻とデータ
    '''
    if not client:
        raise Exception('No database client object.')
    start = (start_time + timedelta(microseconds=1)).isoformat() if start_time else None
    query = _generate_system_stats_query(
        fields=['cpu_percent', 'mem_available', 'disk_used'], 
        every=every, 
        start=start, 
    )
    timestamp = datetime.now(tz=tz.UTC)
    tables = client.query_api().query(query=query)
    #output = _convert_to_time_delta(timestamp, tables)
    #return timestamp, output
    return timestamp, _convert_tables_to_list(tables)

def get_process_cpu_record_at_time(time: datetime):
    '''DBに保存してあったpsutilで取得したCPU使用率が高いプロセスのリストを指定された時刻で取得する。
    
    Args:
        time (datetime): 取得する時刻

    Returns:
        list[tuple[float, int, str]]: プロセスのCPU使用率、PID、プロセス名
    '''
    if not client:
        raise Exception('No database client object.')
    start_time = (time - timedelta(milliseconds=500)).isoformat()
    end_time = (time + timedelta(milliseconds=500)).isoformat()
    query = f'''
    from(bucket: "{settings.INFLUXDB_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "{_MEASUREMENT_PROCESS_CPU}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["pid", "name", "cpu_percent"])
      |> sort(columns: ["cpu"], desc: true)
    '''
    timestamp = datetime.now(tz=tz.UTC)
    tables = client.query_api().query(query=query)
    return timestamp, _convert_tables_to_list(tables)

# MARK: subroutines

def _generate_system_stats_query(fields: list[str], every: str, start: str|None) -> str:
    field_filter = " or ".join([f'r._field == "{field}"' for field in fields])
    pivot_columns = [f"{field}_max" for field in fields] + [f"{field}_mean" for field in fields]
    pivot_columns_str = ", ".join([f'"{col}"' for col in pivot_columns])

    query = f'''
import "date"
truncated_end = date.truncate(t: now(), unit: {every})
data = from(bucket: "{settings.INFLUXDB_BUCKET}")
  |> range(start: {start if start else "-6h"})
  |> filter(fn: (r) => r._measurement == "{_MEASUREMENT_SYS_STATS}")
  |> filter(fn: (r) => {field_filter})
  |> filter(fn: (r) => r._time < truncated_end)

max_data = data
  |> aggregateWindow(every: {every}, fn: max, createEmpty: false)
  |> map(fn: (r) => ({{r with _stat: "max"}}))

mean_data = data
  |> aggregateWindow(every: {every}, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({{r with _stat: "mean"}}))

union(tables: [max_data, mean_data])
  |> map(fn: (r) => ({{r with _field: r._field + "_" + r._stat}}))
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> keep(columns: ["_time", {pivot_columns_str}])
'''
    return query

def _convert_to_time_delta(timestamp: datetime, tables: TableList) -> list[dict]:
    output = []
    for table in tables:
        for record in table.records:
            record['time_delta'] = (record['_time'] - timestamp).total_seconds()
            output.append(record.values)
    return output

def _convert_tables_to_list(tables: TableList) -> list[dict]:
    output = []
    for table in tables:
        for record in table.records:
            output.append(record.values)
    return output
