from dotenv import load_dotenv
from pathlib import Path
import os
from pydantic import BaseModel

# MARK: environment variables

load_dotenv()

PORT = int(os.environ.get('PORT', 8000))
APP_DEBUG = int(os.environ.get('APP_DEBUG', "0"))
DISK_USAGE_PATH = os.environ.get('DISK_USAGE_PATH', '/')
INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', 'my-secret-token')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'my-org')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'system-metrics')

from .logger import logger
logger.debug(f'【settings.py】 {APP_DEBUG=}')
logger.debug(f'【settings.py】 {DISK_USAGE_PATH=}')
logger.debug(f'【settings.py】 {INFLUXDB_URL=}')
logger.debug(f'【settings.py】 {INFLUXDB_TOKEN=}')
logger.debug(f'【settings.py】 {INFLUXDB_ORG=}')
logger.debug(f'【settings.py】 {INFLUXDB_BUCKET=}')

# MARK: constants

class Duration(BaseModel):
    name: str
    period_start: str
    period_seconds: int
    every: str
    every_seconds: int

DURATIONS = [
    Duration(name='3時間', period_start='-3h', period_seconds=3 * 60 * 60, every='1m', every_seconds=1 * 60), 
    Duration(name='6時間', period_start='-6h', period_seconds=6 * 60 * 60, every='2m', every_seconds=2 * 60), 
    Duration(name='12時間', period_start='-12h', period_seconds=12 * 60 * 60, every='4m', every_seconds=4 * 60), 
    Duration(name='1日', period_start='-1d', period_seconds=1 * 24 * 60 * 60, every='8m', every_seconds=8 * 60), 
    Duration(name='1週間', period_start='-1w', period_seconds=7 * 24 * 60 * 60, every='1h', every_seconds=60 * 60), 
]
