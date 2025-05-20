import psutil
from ..db import database
from ..common import settings

def collect_system_metrics():
    '''psutilで取得したデータをDBに保存する。'''
    database.write_record(
        cpu_percent=psutil.cpu_percent(), 
        mem_available=float(psutil.virtual_memory().available), 
        disk_used=float(psutil.disk_usage(settings.DISK_USAGE_PATH).used), 
    )

def get_mem_total():
    return psutil.virtual_memory().total

def get_disk_total():
    return psutil.disk_usage(settings.DISK_USAGE_PATH).total
