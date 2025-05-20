from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

PORT = int(os.environ.get('PORT', 8000))
APP_DEBUG = int(os.environ.get('APP_DEBUG', "0"))
DISK_USAGE_PATH = os.environ.get('DISK_USAGE_PATH', '/')
INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', 'my-secret-token')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'my-org')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'system-metrics')

print(f'【settings.py】 {APP_DEBUG=}')
print(f'【settings.py】 {DISK_USAGE_PATH=}')
print(f'【settings.py】 {INFLUXDB_URL=}')
print(f'【settings.py】 {INFLUXDB_TOKEN=}')
print(f'【settings.py】 {INFLUXDB_ORG=}')
print(f'【settings.py】 {INFLUXDB_BUCKET=}')
