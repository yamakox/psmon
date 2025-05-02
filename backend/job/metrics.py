import psutil
from ..db import database

def collect_system_metrics():
    '''psutilで取得したデータをDBに保存する。'''
    database.write_record(
        cpu_percent=psutil.cpu_percent(), 
        mem_percent=psutil.virtual_memory().percent, 
    )
