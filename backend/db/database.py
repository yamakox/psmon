from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.flux_table import TableList
from ..common import settings
import time
from datetime import datetime
from dateutil import tz
from typing import Any

client: InfluxDBClient = None

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
_MEASUREMENT = 'system_stats'

def write_record(**kwargs):
    '''psutilで取得したデータをDBのレコードに保存する。'''
    if not client:
        raise Exception('No database client object.')
    point = dict(
        measurement=_MEASUREMENT, 
        fields=kwargs,
        time=time.time_ns()
    )
    (client
        .write_api(write_options=SYNCHRONOUS)
        .write(
            bucket=settings.INFLUXDB_BUCKET, 
            record=point, 
        )
    )

def get_records_by_time():
    '''DBに保存してあったpsutilのデータを時間ごとに取得する。'''
    if not client:
        raise Exception('No database client object.')
    query = _generate_flux_query(
        fields=['cpu_percent', 'mem_available', 'disk_used'], 
        start='-6h', 
        every='10s', 
    )
    tables = client.query_api().query(query=query)
    timestamp = datetime.now(tz=tz.UTC)
    output = convert_to_time_delta(timestamp, tables)
    return timestamp, output

def convert_to_time_delta(timestamp: datetime, tables: TableList) -> list[dict]:
    output = []
    for table in tables:
        for record in table.records:
            record['time_delta'] = (record['_time'] - timestamp).total_seconds()
            output.append(record.values)
    return output

# MARK: subroutines

def _generate_flux_query(fields: list[str],
                        start: str = "-6h", every: str = "6m") -> str:
    field_filter = " or ".join([f'r._field == "{field}"' for field in fields])
    pivot_columns = [f"{field}_max" for field in fields] + [f"{field}_mean" for field in fields]
    pivot_columns_str = ", ".join([f'"{col}"' for col in pivot_columns])

    query = f'''
data = from(bucket: "{settings.INFLUXDB_BUCKET}")
  |> range(start: {start})
  |> filter(fn: (r) => r._measurement == "{_MEASUREMENT}")
  |> filter(fn: (r) => {field_filter})

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
