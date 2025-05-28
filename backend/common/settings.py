from dotenv import load_dotenv
from pathlib import Path
import os
from pydantic import BaseModel

# MARK: environment variables

load_dotenv()

PORT = int(os.environ.get('PORT', 8000))
APP_DEBUG = int(os.environ.get('APP_DEBUG', "0"))
ROOTFS_PATH = os.environ.get('ROOTFS_PATH', '/')
TOP_PROCESS_COUNT = int(os.environ.get('TOP_PROCESS_COUNT', 10))
METRICS_INTERVAL = int(os.environ.get('METRICS_INTERVAL', 6))
INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', 'my-secret-token')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'my-org')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'system-metrics')

# MARK: constants

class Duration(BaseModel):
    name: str
    period_start: str
    period_seconds: int
    every: str
    every_seconds: int

DURATIONS = [
    Duration(name='3 hours', period_start='-3h', period_seconds=3 * 60 * 60, every='1m', every_seconds=1 * 60), 
    Duration(name='6 hours', period_start='-6h', period_seconds=6 * 60 * 60, every='2m', every_seconds=2 * 60), 
    Duration(name='12 hours', period_start='-12h', period_seconds=12 * 60 * 60, every='4m', every_seconds=4 * 60), 
    Duration(name='1 day', period_start='-1d', period_seconds=1 * 24 * 60 * 60, every='8m', every_seconds=8 * 60), 
    Duration(name='1 week', period_start='-1w', period_seconds=7 * 24 * 60 * 60, every='1h', every_seconds=60 * 60), 
]
