import psutil
from pathlib import Path
from ..db import database
from ..common import settings
from ..common.logger import logger
import time

# NOTE: プロセスのCPU使用率を取得するために、ホストの/procを参照している:
# see also: https://www.reddit.com/r/docker/comments/mo9wq5/accessing_host_resources_from_inside_a_container/
psutil.PROCFS_PATH = str(Path(settings.ROOTFS_PATH) / 'proc')

def collect_metrics(init: bool = False):
    '''psutilで取得したデータをDBに保存する。'''
    logger.debug(f'collect_metrics(init={init})')
    if init:
        # 初回はpsutilのキャッシュを作成する
        psutil.cpu_percent()
        _get_top_cpu_processes()
        return
    
    t = time.time_ns()
    database.write_system_stats_record(
        t,
        cpu_percent=psutil.cpu_percent(), 
        mem_available=float(psutil.virtual_memory().available), 
        disk_used=float(psutil.disk_usage(settings.ROOTFS_PATH).used), 
    )
    database.write_process_cpu_record(
        t,
        _get_top_cpu_processes(),
    )

def get_mem_total():
    '''メモリの総容量を取得する。'''
    return psutil.virtual_memory().total

def get_disk_total():
    '''ディスクの総容量を取得する。'''
    return psutil.disk_usage(settings.ROOTFS_PATH).total

def _get_top_cpu_processes(interval: float = None) -> list[tuple[float, int, str]]:
    '''CPU使用率が高いプロセスを取得する。

    Returns:
        list[tuple[float, int, str]]: プロセスのCPU使用率、PID、プロセス名
    '''
    process_list = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent = process.cpu_percent(interval=interval)
            process_list.append((cpu_percent, process.pid, process.name()))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # CPU使用率でソート（降順）し、上位を返す
    top_processes = sorted(process_list, key=lambda x: x[0], reverse=True)[:settings.TOP_PROCESS_COUNT]

    return top_processes
