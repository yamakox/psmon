from influxdb_client import InfluxDBClient, BucketRetentionRules, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.flux_table import TableList
from ..common import settings
from ..common.logger import logger
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

    # 参考: retention periodが1週間のバケットの作成方法
    # DOCKER_INFLUXDB_INIT_RETENTIONで設定できるため、以下のコードは不要になった

    #buckets_api = client.buckets_api()
    #existing_buckets = [b for b in buckets_api.find_buckets().buckets if b.name == settings.INFLUXDB_BUCKET]
    #if not existing_buckets:
    #    retention_rule = BucketRetentionRules(type="expire", every_seconds=60 * 60 * 24 * 7)
    #    buckets_api.create_bucket(
    #        bucket_name=settings.INFLUXDB_BUCKET, 
    #        org=settings.INFLUXDB_ORG, 
    #        retention_rules=[retention_rule]
    #    )

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
            .tag('pid', str(pid))
            .tag('name', name)
            .field('cpu_percent', cpu)
        )
        write_api.write(
            bucket=settings.INFLUXDB_BUCKET, 
            record=point, 
        )

def get_system_stats_records_by_time(duration_index: int = 0, start_time: datetime|None = None):
    '''DBに保存してあったpsutilのデータを時間ごとに取得する。
    
    Args:
        every (str): 時間ごとの間隔
        start_time (datetime|None): 取得する時間の開始時刻、Noneの場合は6時間前(now() - 6h)から取得する

    Returns:
        tuple[datetime, list[dict]]: 取得した時刻とデータ
    '''
    if not client:
        raise Exception('No database client object.')
    if duration_index < 0 or duration_index >= len(settings.DURATIONS):
        raise Exception('Invalid duration index.')
    duration = settings.DURATIONS[duration_index]
    if start_time:
        start = (start_time + timedelta(microseconds=1)).isoformat()
    else:
        start = duration.period_start
    query = _generate_system_stats_query(
        fields=['cpu_percent', 'mem_available', 'disk_used'], 
        every=duration.every, 
        start=start, 
    )
    timestamp = datetime.now(tz=tz.UTC)
    tables = client.query_api().query(query=query)
    #output = _convert_to_time_delta(timestamp, tables)
    #return timestamp, output
    return timestamp, _convert_tables_to_list(tables)

def get_process_cpu_record_at_time(time: datetime, every_seconds: int):
    '''DBに保存してあったpsutilで取得したCPU使用率が高いプロセスのリストを指定された時刻で取得する。
    
    Args:
        time (datetime): 取得する時刻

    Returns:
        tuple[datetime, list[dict]]: 取得した時刻と、PID・プロセス名・CPU使用率のリスト
    '''
    if not client:
        raise Exception('No database client object.')
    start_time = (time - timedelta(seconds=every_seconds)).isoformat()
    end_time = time.isoformat()
    # NOTE: tagはpivotの対象ではないが、行に自動で含まれる。keepで明示的に残す。
    # (tagはPandasのDataFrameにおける「インデックスやカラムの属性情報」に近いイメージ)
    query = f'''
    from(bucket: "{settings.INFLUXDB_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "{_MEASUREMENT_PROCESS_CPU}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> keep(columns: ["pid", "name", "cpu_percent"])
    //  |> sort(columns: ["cpu_percent"], desc: true)
    '''
    timestamp = datetime.now(tz=tz.UTC)
    tables = client.query_api().query(query=query)
    records = _convert_tables_to_list(tables)
    # records = sorted(records, key=lambda x: x['cpu_percent'], reverse=True)
    return timestamp, records

# MARK: subroutines

def _generate_system_stats_query(fields: list[str], every: str, start: str) -> str:
    field_filter = " or ".join([f'r._field == "{field}"' for field in fields])
    pivot_columns = [f"{field}_max" for field in fields] + [f"{field}_mean" for field in fields]
    pivot_columns_str = ", ".join([f'"{col}"' for col in pivot_columns])

    query = f'''
import "date"
truncated_end = date.truncate(t: now(), unit: {every})
data = from(bucket: "{settings.INFLUXDB_BUCKET}")
  |> range(start: {start})
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
