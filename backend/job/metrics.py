import psutil
from ..db import database

def collect_system_metrics():
    '''psutilで取得したデータをDBに保存する。'''
    database.write_record(
        cpu_percent=psutil.cpu_percent(), 
        mem_available=psutil.virtual_memory().available, 
    )

def get_mem_total():
    return psutil.virtual_memory().total
