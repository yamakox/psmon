from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
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
    query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
        |> range(start: -3h)
        |> aggregateWindow(every: 1m, fn: max, createEmpty: false)
        |> filter(fn: (r) => r._measurement == "{_MEASUREMENT}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", "cpu_percent", "mem_available"])
    '''
    tables = client.query_api().query(query=query)
    print(f'{tables=}')
    output = []
    timestamp = datetime.now(tz=tz.UTC)
    for table in tables:
        print(f'{table=}')
        for record in table.records:
            record['time_delta'] = (record['_time'] - timestamp).total_seconds()
            output.append(record.values)
    return timestamp, output
