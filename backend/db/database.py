from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from ..config import settings
import time

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

def get_records():
    '''DBに保存してあったpsutilのデータを取得する。'''
    if not client:
        raise Exception('No database client object.')
    query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "{_MEASUREMENT}")
        |> sort(columns: ["_time"])
    '''
    tables = client.query_api().query(query=query)
    output = []
    for table in tables:
        print(f'{table=}')
        for record in table.records:
            output.append(dict(
                time=record.get_time(), 
                fields=record.get_field(), 
                value=record.get_value(), 
            ))
    return output
